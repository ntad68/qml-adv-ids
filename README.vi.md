# Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks

[![English](https://img.shields.io/badge/English-lightgrey.svg)](README.md)
[![Vietnamese](https://img.shields.io/badge/Vietnamese-blue.svg)](README.vi.md)

Mã nguồn chính thức và mã thực nghiệm cho bài báo:
> **"Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks"**  
> *IEEE ICPADS 2026*  
> Phòng thí nghiệm An toàn Thông tin (InSecLab), Trường Đại học Công nghệ Thông tin, ĐHQG-HCM.

Thông tin bài báo: Quach Tuan Kiet, Le Sy Liem, Le Tran Gia Bao, Nghi Hoang Khoa, Dang Van Huynh, Van-Hau Pham, Phan The Duy, "Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks", The 32nd IEEE International Conference on Parallel and Distributed Systems (ICPADS 2026), Tokyo, Japan.

---

## 📌 Tổng quan

Repo này chứa toàn bộ khung thực nghiệm so sánh các mô hình học máy cổ điển (**CNN**, **SVC**) với các mô hình học máy lượng tử (QML) (**QCNN**, **QSVC**) cho hệ thống phát hiện xâm nhập (IDS) trong mạng IoT.

Chúng tôi đánh giá đầy đủ hai khía cạnh:
1. **Hiệu năng khi không bị tấn công (clean)**: Accuracy, AUC, Precision, Recall và F1-score cơ sở.
2. **Độ bền vững trước tấn công đối kháng**: mức độ dễ bị tổn thương trước các tấn công né tránh white-box và black-box tiên tiến (FGSM, ZOO, HopSkipJump, PGD), sử dụng thư viện Adversarial Robustness Toolbox (ART).

---

## 🗂️ Cấu trúc dự án

```text
├── QCNN/                      # Mạng nơ-ron tích chập lượng tử
│   ├── preprocess_data_qcnn.py   # Giảm chiều (PCA về 4 qubit) & chuẩn hóa MinMax cho tập train
│   ├── preprocess_test_qcnn.py   # Tiền xử lý tập test
│   ├── train_qcnn.py             # Kiến trúc QCNN (ZZFeatureMap + Conv/Pooling) và huấn luyện
│   └── test_QCNN.py              # Đánh giá clean (Accuracy, AUC, F1, Precision, Recall)
│
├── QSVC/                      # Bộ phân loại vector hỗ trợ lượng tử
│   ├── precompute.py             # Module 1: Tính trước ma trận Quantum Kernel (chịu lỗi & đa tiến trình)
│   ├── train.py                  # Module 2: Huấn luyện QSVC nhanh từ kernel đã tính sẵn (.dill)
│   └── test.py                   # Module 3: Đánh giá trên kernel test đã tính sẵn (ROC, Confusion Matrix)
│
├── CNN/                       # Mô hình 1D-CNN cổ điển (baseline)
│   ├── train_cnn.py              # Kiến trúc 1D-CNN, biến đổi log đặc trưng và huấn luyện
│   └── test_CNN.py               # Đánh giá trên tập test (Classification Report, ROC-AUC)
│
├── SVC/                       # Mô hình Linear SVC cổ điển (baseline)
│   ├── train_svc.py              # Huấn luyện LinearSVC với trọng số lớp cân bằng
│   └── test_SVC.py               # Kiểm thử và đánh giá baseline
│
├── data_preparation/          # CSV ACI-IoT-2023 gốc -> 8 đặc trưng tỷ lệ + chia train/test
│   └── prepare_aci_iot_dataset.py
│
├── ADVERSARIAL_ATTACK/        # Tấn công đối kháng & đánh giá độ bền vững (ART)
│   ├── art_qcnn.py               # Tấn công né tránh lên QCNN (FGSM, PGD, HopSkipJump, ZOO)
│   ├── fgsm-parallel-loky.py     # Fast Gradient Sign Method lên QSVC (lọc Support Vector & đa lõi)
│   ├── run-art-qsvc-zoo-sv.py    # Tấn công black-box Zeroth-Order Optimization (ZOO) lên QSVC
│   ├── hsj-new.py                # Tấn công black-box dựa trên quyết định HopSkipJump lên QSVC
│   └── eval-hsj.py               # Gộp & đánh giá kết quả HopSkipJump (dùng trên Slurm HPC)
│
├── requirements.txt           # Phiên bản thư viện đã được cố định và kiểm thử
├── LICENSE                    # Giấy phép Apache-2.0
├── .gitignore
├── README.md                  # Bản tiếng Anh
└── README.vi.md               # Bản tiếng Việt
```

---

## ⚙️ Yêu cầu & cài đặt

Đã kiểm thử với Python 3.13 và các phiên bản cố định trong `requirements.txt`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Quy trình chạy

Mọi lệnh đều chạy từ thư mục gốc của repo. Dữ liệu sinh ra nằm trong `data/`, mô hình và kết quả nằm trong `runs/` và `checkpoints/`; cả ba thư mục đều đã được git bỏ qua.

### 0. Chuẩn bị dữ liệu (ACI-IoT-2023 gốc)

Bài báo dùng 8 đặc trưng tỷ lệ Fwd/Bwd (FDiR, FPR, FDuR, FPRR, FITR, FPLR, FLRR, FTRLR). Các file CSV đã xử lý không được công bố, nên script này **tính xấp xỉ** chúng từ các cột CICFlowMeter của file công khai `ACI-IoT-2023.csv`:

```bash
python data_preparation/prepare_aci_iot_dataset.py --raw_csv /path/to/ACI-IoT-2023.csv
```

Script giữ lại các luồng TCP/UDP, loại bỏ dòng inf/NaN và dòng trùng lặp, gán nhãn `Attack_label = (Label != "Benign")`, rồi ghi vào `data/raw/`:
- `test_full.csv`: 55% dữ liệu giữ lại để test, chia phân tầng (khoảng 515 nghìn dòng)
- `test_5000.csv`: tập con phân tầng để chạy nhanh
- `train_{500,1000}_seed{0,42,100,999,2024}.csv`: các tập train nhỏ, chia phân tầng

> ⚠️ Cách ánh xạ đặc trưng chỉ là xấp xỉ (ví dụ: FTRLR dùng tỷ lệ kích thước segment thay cho độ dài TLS record), nên kết quả sẽ không khớp hoàn toàn với bài báo.

### 1. Tiền xử lý cho mô hình lượng tử (log1p → PCA(4) → MinMax)

PCA và scaler chỉ được fit trên tập train rồi dùng lại cho tập test. Dùng `[0, π]` cho QCNN và `[0, 1]` cho QSVC:

```bash
# QCNN
python QCNN/preprocess_data_qcnn.py --input_csv data/raw/train_500_seed42.csv \
    --output_csv data/qcnn/train_500_seed42.csv --bundle_out data/qcnn/preprocessors_500_seed42.joblib --feature_range pi
python QCNN/preprocess_test_qcnn.py --input_csv data/raw/test_5000.csv \
    --output_csv data/qcnn/test_5000.csv --bundle data/qcnn/preprocessors_500_seed42.joblib

# QSVC (các script QSVC đọc dữ liệu từ data/train/ và data/test/)
python QCNN/preprocess_data_qcnn.py --input_csv data/raw/train_500_seed42.csv \
    --output_csv data/train/train_500_seed42.csv --bundle_out data/qsvc/preprocessors_500_seed42.joblib --feature_range 1
python QCNN/preprocess_test_qcnn.py --input_csv data/raw/test_5000.csv \
    --output_csv data/test/test_5000.csv --bundle data/qsvc/preprocessors_500_seed42.joblib
```

### 2. Mô hình cổ điển (CNN & SVC)

Mô hình cổ điển dùng trực tiếp 8 đặc trưng tỷ lệ gốc (log1p + StandardScaler):

```bash
python SVC/train_svc.py --train_csv data/raw/train_500_seed42.csv \
    --scaler_out runs/classical/svc_scaler.pkl --model_out runs/classical/svc_model.pkl
python SVC/test_SVC.py --test_csv data/raw/test_full.csv \
    --scaler_path runs/classical/svc_scaler.pkl --model_path runs/classical/svc_model.pkl

python CNN/train_cnn.py --train_csv data/raw/train_500_seed42.csv \
    --scaler_out runs/classical/cnn_scaler.pkl --model_out runs/classical/cnn_model.keras
python CNN/test_CNN.py --test_csv data/raw/test_full.csv \
    --scaler_path runs/classical/cnn_scaler.pkl --model_path runs/classical/cnn_model.keras
```

### 3. Mô hình lượng tử (QCNN & QSVC)

- **QCNN** (bộ tối ưu SPSA; bài báo dùng 200 vòng lặp):
  ```bash
  python QCNN/train_qcnn.py --train_csv data/qcnn/train_500_seed42.csv --model_out runs/qcnn/qcnn_500_seed42.pkl --maxiter 200
  python QCNN/test_QCNN.py --model_path runs/qcnn/qcnn_500_seed42.pkl --test_csv data/qcnn/test_5000.csv
  ```
- **QSVC** (quy trình 3 bước; tên file tính tương đối so với `data/train/` và `data/test/`):
  ```bash
  # Bước 1: Tính trước quantum kernel (các block checkpoint nằm trong checkpoints/<version>/)
  python QSVC/precompute.py --dataset_train train_500_seed42.csv --dataset_test test_5000.csv --version_name v1 --n_jobs 8

  # Bước 2: Huấn luyện QSVC trên kernel đã tính (mô hình lưu tại runs/checkpoint-test/<version>/model.dill)
  python QSVC/train.py --dataset_train train_500_seed42.csv --version_name v1

  # Bước 3: Đánh giá QSVC
  python QSVC/test.py --dataset_test test_5000.csv --version_name v1
  ```

### 4. Đánh giá độ bền vững trước tấn công đối kháng

`--test_size` là số mẫu test (chọn phân tầng) bị tấn công (bài báo dùng 1000; ZOO và HSJ trên QSVC chạy chậm hơn nhiều). Các script tấn công QSVC đọc số CPU từ biến `SLURM_CPUS_PER_TASK` (mặc định là 1):

```bash
# FGSM / PGD / ZOO / HopSkipJump lên QCNN
python ADVERSARIAL_ATTACK/art_qcnn.py --model_path runs/qcnn/qcnn_500_seed42.pkl \
    --test_csv data/qcnn/test_5000.csv --output_csv runs/qcnn/adv_results.csv --test_size 1000

export SLURM_CPUS_PER_TASK=8
QSVC_ARGS=(--dataset_train train_500_seed42.csv --dataset_test test_5000.csv --version_name v1)

# FGSM / PGD và ZOO lên QSVC (kết quả nằm trong runs/checkpoint-test/v1/)
python ADVERSARIAL_ATTACK/fgsm-parallel-loky.py "${QSVC_ARGS[@]}" --test_size 1000
python ADVERSARIAL_ATTACK/run-art-qsvc-zoo-sv.py "${QSVC_ARGS[@]}" --test_size 100

# HopSkipJump lên QSVC: sinh mẫu đối kháng (có thể chia nhỏ bằng --start_idx/--end_idx), rồi gộp kết quả
python ADVERSARIAL_ATTACK/hsj-new.py "${QSVC_ARGS[@]}" --test_size 1000 \
    --output_npy runs/hsj/hsj_part0.npy --log_file runs/hsj/hsj_part0.log
python ADVERSARIAL_ATTACK/eval-hsj.py "${QSVC_ARGS[@]}" --test_size 1000 \
    --npy_files runs/hsj/hsj_part0.npy --output_csv runs/hsj/hsj_results.csv
```

---

## 📄 Giấy phép
Dự án được phát hành theo giấy phép Apache License 2.0 – xem chi tiết trong file [LICENSE](LICENSE).
