import os
import argparse
import pandas as pd
import numpy as np
import joblib

# ==========================================
# 1. CẤU HÌNH (THAM SỐ DÒNG LỆNH)
# ==========================================
parser = argparse.ArgumentParser(description="Transform tập test bằng PCA & Scaler đã fit trên tập train")
parser.add_argument('--input_csv', type=str, required=True, help="File test 8 đặc trưng tỷ lệ + Attack_label (vd: data/raw/test_full.csv)")
parser.add_argument('--output_csv', type=str, required=True, help="File test đã xử lý (4 đặc trưng + Attack_label)")
parser.add_argument('--bundle', type=str, required=True, help="File .joblib sinh ra bởi preprocess_data_qcnn.py")
args = parser.parse_args()

print(f"--- BẮT ĐẦU QUY TRÌNH: {args.input_csv} ---")
df = pd.read_csv(args.input_csv, skipinitialspace=True)
df.columns = df.columns.str.strip()
X_sample = df.drop(columns=['Attack_label'])
y_sample = df['Attack_label']

log_features = ['FPR', 'FPLR', 'FTRLR', 'FLRR', 'FDiR']
X_sample[log_features] = np.log1p(X_sample[log_features])

# ==========================================
# 2. CHỈ TRANSFORM BẰNG PCA & SCALER ĐÃ TRAIN
# ==========================================
bundle = joblib.load(args.bundle)
pca = bundle["pca"]
scaler = bundle["scaler"]

print("\n⚙️ Transform dữ liệu bằng PCA & Scaler đã train...")
X_sample_pca = pca.transform(X_sample)
X_sample_scaled = scaler.transform(X_sample_pca)

print(f"   -> Kích thước sau xử lý: {X_sample_scaled.shape}")

# ==========================================
# 3. XUẤT FILE PROCESSED (CHO QUANTUM)
# ==========================================
cols_quantum = [f"Feature_{i+1}" for i in range(X_sample_scaled.shape[1])]
df_export_quantum = pd.DataFrame(X_sample_scaled, columns=cols_quantum)
df_export_quantum['Attack_label'] = y_sample.values

os.makedirs(os.path.dirname(os.path.abspath(args.output_csv)), exist_ok=True)
print(f"💾 Đang lưu dữ liệu đã xử lý: {args.output_csv}...")
df_export_quantum.to_csv(args.output_csv, index=False)

print("\n=== ✅ HOÀN TẤT ===")
