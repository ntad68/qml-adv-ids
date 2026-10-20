"""
======================================================================
DU AN: IDS LUONG TU - MODULE 0: CHUAN BI DU LIEU TU ACI-IoT-2023 GOC
FILE: data_preparation/prepare_aci_iot_dataset.py
MO TA:
  - Doc file ACI-IoT-2023.csv goc (dinh dang CICFlowMeter, 85 cot).
  - Tinh XAP XI 8 dac trung ty le (FDiR, FPR, FDuR, FPRR, FITR, FPLR,
    FLRR, FTRLR) tu cac cot thong ke luong. Day KHONG phai file da xu ly
    cua tac gia, nen ket qua se khong trung khop tuyet doi voi bai bao.
  - Gan nhan nhi phan Attack_label = (Label != "Benign").
  - Chia stratified thanh train pool / test, sau do lay mau cac tap
    train nho (500, 1000, ...) theo nhieu seed nhu trong bai bao.
======================================================================
"""

import os
import argparse
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Thu tu cot phai giu nguyen: cac script QSVC lay iloc[:, :-1] lam dac trung va iloc[:, -1] lam nhan
FEATURE_COLUMNS = ['FDiR', 'FPR', 'FDuR', 'FPRR', 'FITR', 'FPLR', 'FLRR', 'FTRLR']
LABEL_COLUMN = 'Attack_label'


def safe_ratio(numerator, denominator):
    """Ty le an toan: a / (b + 1) de tranh chia cho 0 khi luong khong co chieu nguoc (Bwd = 0)."""
    return numerator / (denominator + 1.0)


def compute_ratio_features(df):
    """Anh xa XAP XI cac cot CICFlowMeter sang 8 dac trung ty le Fwd/Bwd cua bai bao."""
    # Toc do byte (byte/giay) theo tung chieu, IAT tinh bang micro-giay
    fwd_byte_rate = 1e6 * df['Total Length of Fwd Packet'] / (df['Fwd IAT Total'] + 1.0)
    bwd_byte_rate = 1e6 * df['Total Length of Bwd Packet'] / (df['Bwd IAT Total'] + 1.0)

    features = pd.DataFrame({
        # Ty le dung luong theo chieu (payload + header)
        'FDiR': safe_ratio(df['Total Length of Fwd Packet'] + df['Fwd Header Length'],
                           df['Total Length of Bwd Packet'] + df['Bwd Header Length']),
        # Ty le so goi tin
        'FPR': safe_ratio(df['Total Fwd Packet'], df['Total Bwd packets']),
        # Ty le thoi luong hoat dong
        'FDuR': safe_ratio(df['Fwd IAT Total'], df['Bwd IAT Total']),
        # Ty le toc do goi tin
        'FPRR': safe_ratio(df['Fwd Packets/s'], df['Bwd Packets/s']),
        # Ty le khoang cach trung binh giua cac goi tin
        'FITR': safe_ratio(df['Fwd IAT Mean'], df['Bwd IAT Mean']),
        # Ty le tong do dai payload
        'FPLR': safe_ratio(df['Total Length of Fwd Packet'], df['Total Length of Bwd Packet']),
        # Ty le toc do byte
        'FLRR': safe_ratio(fwd_byte_rate, bwd_byte_rate),
        # Proxy cho ty le do dai TLS record: kich thuoc segment trung binh
        'FTRLR': safe_ratio(df['Fwd Segment Size Avg'], df['Bwd Segment Size Avg']),
    }, index=df.index)

    # CICFlowMeter doi khi sinh gia tri am (IAT loi) -> cat ve 0 de log1p khong bi NaN
    return features.clip(lower=0).astype(np.float64)


def load_and_clean(raw_csv):
    logging.info(f"Dang doc du lieu goc: {raw_csv}")
    df = pd.read_csv(raw_csv, low_memory=False)
    df.columns = df.columns.str.strip()
    logging.info(f"  -> {len(df):,} dong, {df.shape[1]} cot")

    # Chi giu TCP (6) va UDP (17): cac dac trung ty le Fwd/Bwd chi co nghia voi luong 2 chieu
    df = df[df['Protocol'].isin([6, 17])]
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    df = df.drop_duplicates()
    logging.info(f"  -> Sau khi loc TCP/UDP, bo inf/NaN va trung lap: {len(df):,} dong")

    out = compute_ratio_features(df)
    out[LABEL_COLUMN] = (df['Label'].astype(str).str.strip() != 'Benign').astype(int)
    return out.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Chuan bi du lieu ACI-IoT-2023 goc thanh 8 dac trung ty le")
    parser.add_argument('--raw_csv', type=str, required=True, help="Duong dan toi ACI-IoT-2023.csv goc")
    parser.add_argument('--out_dir', type=str, default=os.path.join(REPO_ROOT, 'data', 'raw'))
    parser.add_argument('--test_frac', type=float, default=0.55, help="Ty le du lieu danh cho tap test day du")
    parser.add_argument('--train_sizes', type=int, nargs='+', default=[500, 1000])
    parser.add_argument('--seeds', type=int, nargs='+', default=[0, 42, 100, 999, 2024])
    parser.add_argument('--test_subset_size', type=int, default=5000,
                        help="Kich thuoc tap test nho (stratified) de chay thu nhanh")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = load_and_clean(args.raw_csv)
    logging.info(f"Phan bo nhan: {df[LABEL_COLUMN].value_counts().to_dict()}")

    train_pool, test_full = train_test_split(
        df, test_size=args.test_frac, stratify=df[LABEL_COLUMN], random_state=42
    )
    test_full.to_csv(os.path.join(args.out_dir, 'test_full.csv'), index=False)
    logging.info(f"Da luu test_full.csv ({len(test_full):,} dong)")

    _, test_subset = train_test_split(
        test_full, test_size=args.test_subset_size, stratify=test_full[LABEL_COLUMN], random_state=42
    )
    test_subset_name = f"test_{args.test_subset_size}.csv"
    test_subset.to_csv(os.path.join(args.out_dir, test_subset_name), index=False)
    logging.info(f"Da luu {test_subset_name}")

    for size in args.train_sizes:
        for seed in args.seeds:
            train_sample, _ = train_test_split(
                train_pool, train_size=size, stratify=train_pool[LABEL_COLUMN], random_state=seed
            )
            name = f"train_{size}_seed{seed}.csv"
            train_sample.to_csv(os.path.join(args.out_dir, name), index=False)
            logging.info(f"Da luu {name}")

    logging.info(f"=== HOAN TAT. Du lieu nam tai: {args.out_dir} ===")


if __name__ == "__main__":
    main()
