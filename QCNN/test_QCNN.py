import argparse
import dill
import pandas as pd
import numpy as np
from sklearn.metrics import (roc_auc_score, confusion_matrix, f1_score,  classification_report, precision_score, recall_score, accuracy_score) 
parser = argparse.ArgumentParser(description="Đánh giá QCNN trên tập test sạch")
parser.add_argument('--model_path', type=str, required=True, help="File mô hình .pkl sinh ra bởi train_qcnn.py")
parser.add_argument('--test_csv', type=str, required=True, help="File test đã qua preprocess_test_qcnn.py")
args = parser.parse_args()

# =========================
# 1. Load QCNN model
# =========================
with open(args.model_path, "rb") as f:
    classifier = dill.load(f)

print("Model loaded")

# =========================
# 2. Load dataset test
# =========================
df_test = pd.read_csv(args.test_csv)

# Đảm bảo bỏ đúng cột label, kiểm tra lại tên cột "Attack_label"
X_test = df_test.drop(columns=["Attack_label"]).values
y_test = df_test["Attack_label"].values

# =========================
# 3. Predict (Xác suất)
# =========================
probs = classifier.predict_proba(X_test)[:, 1]

# =========================
# 4. Chuyển đổi nhãn với Threshold = 0.5
# =========================
threshold = 0.5
y_pred = (probs >= threshold).astype(int)

# =========================
# 5. Evaluate (Đánh giá chi tiết)
# =========================
auc = roc_auc_score(y_test, probs)
acc = accuracy_score(y_test, y_pred) # Thêm Accuracy
f1 = f1_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

# =========================
# 6. In kết quả (Đã tối ưu để copy vào bài báo)
# =========================
print("\n" + "="*50)
print(f"{'BÁO CÁO KẾT QUẢ ĐÁNH GIÁ QCNN':^50}")
print("="*50)
print(f"[*] Accuracy  : {acc:.4f} ({acc*100:.2f}%)")
print(f"[*] AUC Score : {auc:.4f}")
print(f"[*] F1-Score  : {f1:.4f}")
print(f"[*] Precision : {prec:.4f}")
print(f"[*] Recall    : {rec:.4f}")

print("-" * 50)
print("CONFUSION MATRIX (Ma trận nhầm lẫn):")
print(f" - True Negative (TN) : {cm[0,0]:<6} | (Đúng là Bình thường)")
print(f" - False Positive (FP): {cm[0,1]:<6} | (Báo động nhầm)")
print(f" - False Negative (FN): {cm[1,0]:<6} | (Bỏ lọt tấn công - Cảnh báo!)")
print(f" - True Positive (TP) : {cm[1,1]:<6} | (Bắt đúng tấn công)")
print("-" * 50)

# Phần này vẫn giữ để xem chi tiết từng lớp
print("\nCLASSIFICATION REPORT CHI TIẾT:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
print("="*50)

