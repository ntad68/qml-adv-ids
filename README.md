# Hướng dẫn chạy dự án: Phát hiện tấn công mạng IoT bằng học máy lượng tử

Đây là mã nguồn của bài báo **"Adversarial Robustness of Quantum Learning-based Intrusion Detection Systems in IoT Networks"** (hội nghị IEEE ICPADS 2026), do nhóm InSecLab, Trường ĐH Công nghệ Thông tin, ĐHQG-HCM thực hiện.

Bạn **không cần biết lập trình** để làm theo hướng dẫn này. Chỉ cần **sao chép từng lệnh**, dán vào cửa sổ dòng lệnh (Terminal), nhấn **Enter**, rồi chờ lệnh chạy xong.

---

## Dự án này làm gì?

Hãy tưởng tượng có một "người bảo vệ" theo dõi mạng IoT (camera, cảm biến, thiết bị thông minh...) và báo động khi có kẻ tấn công. Dự án này thử nghiệm hai việc:

1. **Người bảo vệ nào giỏi hơn?** So sánh 2 mô hình máy tính thông thường (**SVC**, **CNN**) với 2 mô hình máy tính lượng tử (**QSVC**, **QCNN**).
2. **Người bảo vệ nào khó bị lừa hơn?** Kẻ tấn công cố tình "ngụy trang" dữ liệu để qua mặt người bảo vệ. Ta đo xem mỗi mô hình bị lừa bao nhiêu lần.

---

## Bạn sẽ làm những gì?

| Bước | Việc cần làm | Thời gian (ước tính) |
|---|---|---|
| 1 | Mở Terminal và vào thư mục dự án | 1 phút |
| 2 | Cài đặt (chỉ làm lần đầu) | 5–15 phút |
| 3 | Chuẩn bị dữ liệu | 5–10 phút |
| 4 | Chạy mô hình thông thường (SVC, CNN) | vài phút |
| 5 | Chuẩn bị dữ liệu cho mô hình lượng tử | dưới 1 phút |
| 6 | Chạy mô hình lượng tử QCNN | vài giờ |
| 7 | Chạy mô hình lượng tử QSVC | vài chục phút đến vài giờ |
| 8 | Thử "lừa" mô hình QCNN | vài giờ |
| 9 | Thử "lừa" mô hình QSVC | vài giờ đến vài ngày |

Hãy làm **đúng thứ tự** từ trên xuống. Bước sau cần kết quả của bước trước.

---

## Một vài điều cần biết trước khi bắt đầu

- **Cách dán lệnh:** bôi đen lệnh trong khung xám, sao chép (Ctrl+C), bấm vào cửa sổ Terminal, dán (thường là **Ctrl+Shift+V** hoặc chuột phải → Paste), rồi nhấn **Enter**.
- **Lệnh dài nhiều dòng:** cứ sao chép **cả khung** và dán một lần, Terminal sẽ hiểu đó là một lệnh.
- **Dòng bắt đầu bằng `#`** chỉ là lời giải thích, máy sẽ bỏ qua. Bạn có thể dán cả dòng đó cũng không sao.
- **Biết lệnh đã chạy xong khi nào?** Khi dòng nhắc lệnh (dấu `$` ở cuối) xuất hiện trở lại và bạn gõ được chữ.
- **Muốn dừng lệnh đang chạy?** Nhấn **Ctrl+C**.
- **Không tắt Terminal** khi lệnh đang chạy, nếu không lệnh sẽ bị dừng.

---

## Bước 1: Mở Terminal và vào thư mục dự án

Mở **Terminal** trên máy chủ, rồi dán đoạn sau:

```bash
cd "/mnt/DiskVM/lost+found/qml-adv-ids-main"
RAW_CSV="/mnt/DiskVM/lost+found/qml-adv-ids-main/ACI-IoT-2023.csv"
ls -lh "$RAW_CSV"
```

✅ **Thành công khi:** dòng cuối hiện ra thông tin file `ACI-IoT-2023.csv` (kích thước, ngày tạo...).

❌ **Nếu báo `No such file or directory`:** file dữ liệu có tên khác hoặc nằm chỗ khác. Gõ `ls` để xem tên các file trong thư mục, rồi sửa lại phần `ACI-IoT-2023.csv` ở dòng thứ hai cho đúng tên.

> 🔁 **Quan trọng:** Mỗi lần mở Terminal mới (ví dụ hôm sau quay lại làm tiếp), bạn phải dán lại đoạn lệnh ở Bước 1, rồi dán thêm lệnh `source .venv/bin/activate` (sau khi đã làm Bước 2).

---

## Bước 2: Cài đặt (chỉ làm lần đầu)

Bước này cài các phần mềm mà dự án cần. Đầu tiên, kiểm tra phiên bản Python:

```bash
python3 --version
```

✅ Cần thấy `Python 3.13.x`. Nếu là phiên bản khác, hãy nhờ người quản trị máy cài Python 3.13 trước.

Sau đó dán lần lượt 3 lệnh sau:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Lệnh cuối sẽ tải và cài nhiều thứ, mất khoảng 5–15 phút.

✅ **Thành công khi:** đầu dòng lệnh có chữ `(.venv)`, và dòng cuối cùng có chữ `Successfully installed ...`.

---

## Bước 3: Chuẩn bị dữ liệu

File dữ liệu gốc rất lớn và có rất nhiều cột. Bước này chỉ lấy những thông tin cần thiết và chia dữ liệu thành phần để **học** (train) và phần để **kiểm tra** (test).

```bash
python data_preparation/prepare_aci_iot_dataset.py --raw_csv "$RAW_CSV"
```

✅ **Thành công khi:** có thư mục mới `data/raw/` chứa các file như `test_full.csv`, `test_5000.csv`, `train_500_seed42.csv`... Kiểm tra bằng lệnh:

```bash
ls data/raw/
```

> ℹ️ Nhóm tác giả không công bố dữ liệu họ đã xử lý, nên bước này chỉ tính **gần đúng**. Vì vậy kết quả của bạn sẽ không giống hệt con số trong bài báo. Đây là điều bình thường.

---

## Bước 4: Chạy mô hình thông thường (SVC và CNN)

Hai mô hình này dùng để so sánh với mô hình lượng tử. Mỗi mô hình gồm 2 việc: **học** từ dữ liệu, rồi **kiểm tra** xem đoán đúng được bao nhiêu.

**4.1 Mô hình SVC:**

```bash
python SVC/train_svc.py --train_csv data/raw/train_500_seed42.csv --scaler_out runs/classical/svc_scaler.pkl --model_out runs/classical/svc_model.pkl
```

```bash
python SVC/test_SVC.py --test_csv data/raw/test_full.csv --scaler_path runs/classical/svc_scaler.pkl --model_path runs/classical/svc_model.pkl
```

**4.2 Mô hình CNN:**

```bash
python CNN/train_cnn.py --train_csv data/raw/train_500_seed42.csv --scaler_out runs/classical/cnn_scaler.pkl --model_out runs/classical/cnn_model.keras
```

```bash
python CNN/test_CNN.py --test_csv data/raw/test_full.csv --scaler_path runs/classical/cnn_scaler.pkl --model_path runs/classical/cnn_model.keras
```

✅ **Thành công khi:** lệnh kiểm tra in ra bảng kết quả có chữ **accuracy** (độ chính xác). Ví dụ `accuracy 0.79` nghĩa là mô hình đoán đúng 79%.

---

## Bước 5: Chuẩn bị dữ liệu cho mô hình lượng tử

Máy tính lượng tử trong dự án này chỉ xử lý được **4 con số** cho mỗi dòng dữ liệu, trong khi dữ liệu đang có 8. Bước này "nén" dữ liệu cho vừa. Dán cả khung sau:

```bash
python QCNN/preprocess_data_qcnn.py --input_csv data/raw/train_500_seed42.csv --output_csv data/qcnn/train_500_seed42.csv --bundle_out data/qcnn/preprocessors_500_seed42.joblib --feature_range pi
python QCNN/preprocess_test_qcnn.py --input_csv data/raw/test_5000.csv --output_csv data/qcnn/test_5000.csv --bundle data/qcnn/preprocessors_500_seed42.joblib
python QCNN/preprocess_data_qcnn.py --input_csv data/raw/train_500_seed42.csv --output_csv data/train/train_500_seed42.csv --bundle_out data/qsvc/preprocessors_500_seed42.joblib --feature_range 1
python QCNN/preprocess_test_qcnn.py --input_csv data/raw/test_5000.csv --output_csv data/test/test_5000.csv --bundle data/qsvc/preprocessors_500_seed42.joblib
```

✅ **Thành công khi:** có các thư mục mới `data/qcnn/`, `data/train/` và `data/test/`.

---

## Bước 6: Chạy mô hình lượng tử QCNN

**6.1 Học** (bước này **lâu**, có thể mất nhiều giờ):

```bash
python QCNN/train_qcnn.py --train_csv data/qcnn/train_500_seed42.csv --model_out runs/qcnn/qcnn_500_seed42.pkl --maxiter 200
```

> 💡 **Muốn chạy thử nhanh trước?** Đổi `--maxiter 200` thành `--maxiter 5`. Chạy sẽ nhanh hơn rất nhiều, nhưng độ chính xác thấp hơn. Khi chạy thật thì để lại `200` như bài báo.

**6.2 Kiểm tra:**

```bash
python QCNN/test_QCNN.py --model_path runs/qcnn/qcnn_500_seed42.pkl --test_csv data/qcnn/test_5000.csv
```

✅ **Thành công khi:** in ra kết quả có chữ **Accuracy**.

---

## Bước 7: Chạy mô hình lượng tử QSVC

QSVC gồm 3 lệnh, chạy lần lượt.

**7.1 Tính toán lượng tử** (bước **lâu nhất** của QSVC):

```bash
python QSVC/precompute.py --dataset_train train_500_seed42.csv --dataset_test test_5000.csv --version_name v1 --n_jobs 8
```

> 💡 `--n_jobs 8` nghĩa là dùng 8 nhân CPU. Máy mạnh hơn thì có thể tăng lên để chạy nhanh hơn.
> 💡 Nếu lệnh bị dừng giữa chừng, chỉ cần dán lại đúng lệnh này, nó sẽ **tiếp tục** từ chỗ đã dừng chứ không chạy lại từ đầu.

**7.2 Học** (rất nhanh):

```bash
python QSVC/train.py --dataset_train train_500_seed42.csv --version_name v1
```

**7.3 Kiểm tra:**

```bash
python QSVC/test.py --dataset_test test_5000.csv --version_name v1
```

✅ **Thành công khi:** in ra kết quả có chữ **Accuracy**.

---

## Bước 8: Thử "lừa" mô hình QCNN

Bước này thử 4 cách lừa khác nhau (tên kỹ thuật: FGSM, PGD, ZOO, HopSkipJump) trên 1000 mẫu dữ liệu.

```bash
python ADVERSARIAL_ATTACK/art_qcnn.py --model_path runs/qcnn/qcnn_500_seed42.pkl --test_csv data/qcnn/test_5000.csv --output_csv runs/qcnn/adv_results.csv --test_size 1000
```

✅ **Thành công khi:** có file kết quả `runs/qcnn/adv_results.csv`. Xem cách đọc kết quả ở cuối trang.

---

## Bước 9: Thử "lừa" mô hình QSVC

**9.1 Chuẩn bị** (dán đoạn này trước, và dán lại nếu mở Terminal mới):

```bash
export SLURM_CPUS_PER_TASK=8
QSVC_ARGS=(--dataset_train train_500_seed42.csv --dataset_test test_5000.csv --version_name v1)
```

**9.2 Cách lừa FGSM và PGD:**

```bash
python ADVERSARIAL_ATTACK/fgsm-parallel-loky.py "${QSVC_ARGS[@]}" --test_size 1000
```

**9.3 Cách lừa ZOO** (chậm hơn, nên chỉ thử 100 mẫu):

```bash
python ADVERSARIAL_ATTACK/run-art-qsvc-zoo-sv.py "${QSVC_ARGS[@]}" --test_size 100
```

Kết quả của 9.2 và 9.3 nằm trong thư mục `runs/checkpoint-test/v1/`.

**9.4 Cách lừa HopSkipJump** (**rất chậm**: khoảng 4 phút cho mỗi mẫu, nên 1000 mẫu có thể mất vài ngày). Gồm 2 lệnh: tạo dữ liệu lừa, rồi chấm điểm.

```bash
python ADVERSARIAL_ATTACK/hsj-new.py "${QSVC_ARGS[@]}" --test_size 1000 --output_npy runs/hsj/hsj_part0.npy --log_file runs/hsj/hsj_part0.log
```

> 💡 Lệnh này **tự lưu tiến độ**. Nếu bị dừng, dán lại đúng lệnh này để chạy tiếp. Dòng `Progress: 25/1000 | ETA: ...` cho biết đã làm được bao nhiêu và còn khoảng bao lâu.
> 💡 Muốn chạy thử nhanh: đổi `--test_size 1000` thành `--test_size 20` ở **cả hai** lệnh 9.4.

Khi lệnh trên chạy xong, chấm điểm:

```bash
python ADVERSARIAL_ATTACK/eval-hsj.py "${QSVC_ARGS[@]}" --test_size 1000 --npy_files runs/hsj/hsj_part0.npy --output_csv runs/hsj/hsj_results.csv
```

✅ **Thành công khi:** có file kết quả `runs/hsj/hsj_results.csv`.

---

## Cách đọc kết quả "lừa" mô hình

Mở các file kết quả `.csv` bằng Excel hoặc Google Sheets. Các cột quan trọng:

| Cột | Ý nghĩa dễ hiểu |
|---|---|
| `Clean_Acc` | Tỷ lệ đoán đúng **khi chưa bị lừa** |
| `Robust_Acc` | Tỷ lệ đoán đúng **sau khi bị lừa** |
| `ASR` | Tỷ lệ **lừa thành công**. Ví dụ `0.36` = lừa được 36% số lần. **Càng thấp càng tốt** (mô hình càng khó bị lừa) |

---

## Gặp lỗi thì làm gì?

| Thông báo lỗi | Cách xử lý |
|---|---|
| `No such file or directory` | Bạn đang không ở đúng thư mục, hoặc chưa làm bước trước đó. Dán lại đoạn lệnh ở **Bước 1**, rồi kiểm tra đã làm đủ các bước trước chưa |
| `ModuleNotFoundError` hoặc `command not found: python` | Chưa bật môi trường cài đặt. Dán lệnh `source .venv/bin/activate` |
| `Khong tim thay ... kernel_train.npy` | Chưa chạy xong bước **7.1** |
| Báo không tìm thấy `model.dill` | Chưa chạy xong **Bước 7** |
| Chạy mãi không xong | Bình thường với các bước lượng tử. Xem gợi ý "chạy thử nhanh" ở từng bước |

Nếu vẫn không được, hãy chụp màn hình thông báo lỗi và gửi cho người hỗ trợ kỹ thuật.

---

## Giấy phép

Dự án dùng giấy phép Apache License 2.0, xem file [LICENSE](LICENSE).
