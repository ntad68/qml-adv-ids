import os
import argparse
import pandas as pd
import numpy as np
import joblib
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

# ==========================================
# 1. CẤU HÌNH (THAM SỐ DÒNG LỆNH)
# ==========================================
parser = argparse.ArgumentParser(description="Fit log1p + PCA(4) + MinMax trên tập train và xuất dữ liệu cho mô hình lượng tử")
parser.add_argument('--input_csv', type=str, required=True, help="File train 8 đặc trưng tỷ lệ + Attack_label (vd: data/raw/train_500_seed42.csv)")
parser.add_argument('--output_csv', type=str, required=True, help="File train đã xử lý (4 đặc trưng + Attack_label)")
parser.add_argument('--bundle_out', type=str, required=True, help="File .joblib lưu PCA & Scaler để dùng lại cho tập test")
parser.add_argument('--feature_range', choices=['pi', '1'], default='pi',
                    help="'pi' -> [0, π] cho QCNN; '1' -> [0, 1] cho QSVC")
args = parser.parse_args()

upper = np.pi if args.feature_range == 'pi' else 1.0

print(f"--- BẮT ĐẦU QUY TRÌNH: {args.input_csv} ---")
df = pd.read_csv(args.input_csv, skipinitialspace=True)
df.columns = df.columns.str.strip()
X_sample = df.drop(columns=['Attack_label'])
y_sample = df['Attack_label']

log_features = ['FPR', 'FPLR', 'FTRLR', 'FLRR', 'FDiR']
X_sample[log_features] = np.log1p(X_sample[log_features])

# ==========================================
# 2. FIT PCA & SCALER
# ==========================================
print(f"\n⚙️ Đang áp dụng PCA (n=4) và Scaler [0, {args.feature_range}]...")

# 1. Giảm chiều xuống 4 (để khớp với 4 Qubit theo bài báo)
pca = PCA(n_components=4)
X_sample_pca = pca.fit_transform(X_sample)

# 2. Chuẩn hóa về [0, π] (QCNN) hoặc [0, 1] (QSVC) cho Rotation Encoding
scaler = MinMaxScaler(feature_range=(0, upper))
X_sample_scaled = scaler.fit_transform(X_sample_pca)

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

# ==========================================
# 4. LƯU LẠI PCA & SCALER (QUAN TRỌNG)
# ==========================================
# Lưu lại để tập test dùng đúng hệ quy chiếu đã fit trên tập train
os.makedirs(os.path.dirname(os.path.abspath(args.bundle_out)), exist_ok=True)
print(f"💾 Đang lưu PCA & Scaler vào '{args.bundle_out}'...")
joblib.dump({'pca': pca, 'scaler': scaler}, args.bundle_out)

print("\n=== ✅ HOÀN TẤT ===")
