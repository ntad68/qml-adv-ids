# Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks

Official implementation and experimental code for the paper:
> **"Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks"**  
> *IEEE ICPADS 2026*  
> Information Security Laboratory (InSecLab), VNU-HCM University of Information Technology.

The details of the paper: Quach Tuan Kiet, Le Sy Liem, Le Tran Gia Bao, Nghi Hoang Khoa, Dang Van Huynh, Van-Hau Pham, Phan The Duy, "Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks", The 32nd IEEE International Conference on Parallel and Distributed Systems (ICPADS 2026), Tokyo, Japan.
---

## 📌 Overview

This repository provides the complete experimental framework comparing classical machine learning models (**CNN**, **SVC**) against Quantum Machine Learning (QML) models (**QCNN**, **QSVC**) for Intrusion Detection Systems (IDS) in IoT networks.

We comprehensively evaluate both:
1. **Clean Performance**: Baseline detection accuracy, AUC, Precision, Recall, and F1-score without attacks.
2. **Adversarial Robustness**: Vulnerability and robustness against state-of-the-art white-box and black-box evasion attacks (FGSM, ZOO, HopSkipJump, PGD) utilizing the Adversarial Robustness Toolbox (ART).

---

## 🗂️ Project Structure

```text
├── QCNN/                      # Quantum Convolutional Neural Network
│   ├── preprocess_data_qcnn.py   # Dimensionality reduction (PCA to 4 qubits) & MinMax scaling for train set
│   ├── preprocess_test_qcnn.py   # Test set preprocessing pipeline
│   ├── train_qcnn.py             # QCNN architecture design (ZZFeatureMap + Conv/Pooling) and training
│   └── test_QCNN.py              # Clean evaluation metrics (Accuracy, AUC, F1, Precision, Recall)
│
├── QSVC/                      # Quantum Support Vector Classifier
│   ├── precompute.py             # Module 1: Precomputes Quantum Kernel matrices with fault-tolerance & multiprocessing
│   ├── train.py                  # Module 2: Fast QSVC training using precomputed kernels (.dill)
│   └── test.py                   # Module 3: Evaluation on precomputed test kernels (ROC, Confusion Matrix)
│
├── CNN/                       # Classical 1D-CNN Baseline
│   ├── train_cnn.py              # 1D-CNN model architecture, log feature transformation, and training
│   └── test_CNN.py               # Evaluation on test dataset (Classification Report, ROC-AUC)
│
├── SVC/                       # Classical Linear SVC Baseline
│   ├── train_svc.py              # LinearSVC model training with balanced class weights
│   └── test_SVC.py               # Baseline testing and evaluation
│
├── data_preparation/          # Raw ACI-IoT-2023 CSV -> 8 ratio features + train/test splits
│   └── prepare_aci_iot_dataset.py
│
├── ADVERSARIAL_ATTACK/        # Adversarial Attacks & Robustness Evaluation (ART)
│   ├── art_qcnn.py               # Evasion attacks on QCNN (FGSM, PGD, HopSkipJump, ZOO)
│   ├── fgsm-parallel-loky.py     # Fast Gradient Sign Method on QSVC (Support Vector filtering & multi-core)
│   ├── run-art-qsvc-zoo-sv.py    # Zeroth-Order Optimization (ZOO) black-box attack on QSVC
│   ├── hsj-new.py                # HopSkipJump decision-based black-box attack on QSVC
│   └── eval-hsj.py               # Aggregation & evaluation script for HopSkipJump on Slurm HPC
│
├── requirements.txt           # Pinned, tested dependency versions
├── LICENSE                    # Apache-2.0 License
├── .gitignore
└── README.md
```

---

## ⚙️ Requirements & Installation

Tested with Python 3.13 and the versions pinned in `requirements.txt`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Workflow

All commands are run from the repository root. Generated data goes to `data/`, models and results go to `runs/` and `checkpoints/`; all three are git-ignored.

### 0. Data Preparation (raw ACI-IoT-2023)

The paper uses 8 Fwd/Bwd ratio features (FDiR, FPR, FDuR, FPRR, FITR, FPLR, FLRR, FTRLR). The processed CSVs are not distributed, so this script **approximates** them from the CICFlowMeter columns of the public `ACI-IoT-2023.csv`:

```bash
python data_preparation/prepare_aci_iot_dataset.py --raw_csv /path/to/ACI-IoT-2023.csv
```

It keeps TCP/UDP flows, drops inf/NaN rows and duplicates, labels `Attack_label = (Label != "Benign")`, and writes to `data/raw/`:
- `test_full.csv`: 55% stratified hold-out (about 515k rows)
- `test_5000.csv`: stratified subset for quick runs
- `train_{500,1000}_seed{0,42,100,999,2024}.csv`: small stratified training sets

> ⚠️ The feature mapping is an approximation (e.g. FTRLR uses the segment-size ratio as a proxy for TLS record length), so numbers will not exactly match the paper.

### 1. Quantum Preprocessing (log1p → PCA(4) → MinMax)

PCA and the scaler are fitted on the training set only and reused for the test set. Use `[0, π]` for QCNN and `[0, 1]` for QSVC:

```bash
# QCNN
python QCNN/preprocess_data_qcnn.py --input_csv data/raw/train_500_seed42.csv \
    --output_csv data/qcnn/train_500_seed42.csv --bundle_out data/qcnn/preprocessors_500_seed42.joblib --feature_range pi
python QCNN/preprocess_test_qcnn.py --input_csv data/raw/test_5000.csv \
    --output_csv data/qcnn/test_5000.csv --bundle data/qcnn/preprocessors_500_seed42.joblib

# QSVC (QSVC scripts read from data/train/ and data/test/)
python QCNN/preprocess_data_qcnn.py --input_csv data/raw/train_500_seed42.csv \
    --output_csv data/train/train_500_seed42.csv --bundle_out data/qsvc/preprocessors_500_seed42.joblib --feature_range 1
python QCNN/preprocess_test_qcnn.py --input_csv data/raw/test_5000.csv \
    --output_csv data/test/test_5000.csv --bundle data/qsvc/preprocessors_500_seed42.joblib
```

### 2. Classical Models (CNN & SVC)

Classical models use the 8 raw ratio features directly (log1p + StandardScaler):

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

### 3. Quantum Models (QCNN & QSVC)

- **QCNN** (SPSA optimizer; the paper uses 200 iterations):
  ```bash
  python QCNN/train_qcnn.py --train_csv data/qcnn/train_500_seed42.csv --model_out runs/qcnn/qcnn_500_seed42.pkl --maxiter 200
  python QCNN/test_QCNN.py --model_path runs/qcnn/qcnn_500_seed42.pkl --test_csv data/qcnn/test_5000.csv
  ```
- **QSVC** (3-stage pipeline; file names are relative to `data/train/` and `data/test/`):
  ```bash
  # Step 1: Precompute quantum kernels (checkpointed blocks in checkpoints/<version>/)
  python QSVC/precompute.py --dataset_train train_500_seed42.csv --dataset_test test_5000.csv --version_name v1 --n_jobs 8

  # Step 2: Train QSVC on the precomputed kernel (model saved to runs/checkpoint-test/<version>/model.dill)
  python QSVC/train.py --dataset_train train_500_seed42.csv --version_name v1

  # Step 3: Evaluate QSVC
  python QSVC/test.py --dataset_test test_5000.csv --version_name v1
  ```

### 4. Adversarial Robustness Assessment

`--test_size` is the number of stratified test samples attacked (the paper uses 1000; ZOO and HSJ on QSVC are much slower). QSVC attack scripts read the CPU count from `SLURM_CPUS_PER_TASK` (default 1):

```bash
# FGSM / PGD / ZOO / HopSkipJump on QCNN
python ADVERSARIAL_ATTACK/art_qcnn.py --model_path runs/qcnn/qcnn_500_seed42.pkl \
    --test_csv data/qcnn/test_5000.csv --output_csv runs/qcnn/adv_results.csv --test_size 1000

export SLURM_CPUS_PER_TASK=8
QSVC_ARGS=(--dataset_train train_500_seed42.csv --dataset_test test_5000.csv --version_name v1)

# FGSM / PGD and ZOO on QSVC (results in runs/checkpoint-test/v1/)
python ADVERSARIAL_ATTACK/fgsm-parallel-loky.py "${QSVC_ARGS[@]}" --test_size 1000
python ADVERSARIAL_ATTACK/run-art-qsvc-zoo-sv.py "${QSVC_ARGS[@]}" --test_size 100

# HopSkipJump on QSVC: generate (can be sharded with --start_idx/--end_idx), then aggregate
python ADVERSARIAL_ATTACK/hsj-new.py "${QSVC_ARGS[@]}" --test_size 1000 \
    --output_npy runs/hsj/hsj_part0.npy --log_file runs/hsj/hsj_part0.log
python ADVERSARIAL_ATTACK/eval-hsj.py "${QSVC_ARGS[@]}" --test_size 1000 \
    --npy_files runs/hsj/hsj_part0.npy --output_csv runs/hsj/hsj_results.csv
```

---

## 📄 License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
