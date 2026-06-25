# HUONG DAN CHAY LENH VA CHUP ANH NOP BAI

File nay huong dan tung buoc de ban tu chay lab, mo web, chup anh bang chung va nop bai.

Quan trong:

- Khong dung script tao anh tu dong.
- Moi anh nop bai phai la anh ban tu chup tu terminal, MLflow UI, GitHub Actions, AWS Console, DagsHub.
- Neu dung Windows PowerShell, hay copy dung cac lenh trong file nay.
- Thay cac gia tri trong dau `<...>` bang thong tin that cua ban.

Repo nop bai:

```text
https://github.com/edward1503/Day21-Track2-CI-CD-for-AI-Systems
```

Thu muc anh nop bai:

```text
submission/screenshots/
```

Ten anh nen dung:

```text
Task1-MlflowRun.png
Task1-DVCS3.png
Task2-GithubActionsFlow.png
Task2-CheckEvalGate.png
Task2-EC2Curl.png
Task3-NewActions.png
Task3-EvalGatePass.png
BONUS-1.png
BONUS-2.png
BONUS-3.png
BONUS-4.png
BONUS-5.png
```

---

## 1. Chuan bi moi truong local

Mo PowerShell tai thu muc project:

```powershell
cd "C:\Users\Thanh Danh\Desktop\Day21-Track2-CI-CD-for-AI-Systems"
```

Tao va kich hoat moi truong ao:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Neu PowerShell bao loi policy khi activate, chay:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Cai thu vien:

```powershell
python -m pip install -r requirements.txt
```

Tao du lieu ban dau:

```powershell
python generate_data.py
```

Ket qua mong doi:

```text
train_phase1.csv : 2998 mau
eval.csv         : 500 mau
train_phase2.csv : 2998 mau
```

Kiem tra file data:

```powershell
Get-ChildItem data
```

Chay test local:

```powershell
mkdir .tmp -ErrorAction SilentlyContinue
$env:TMP = "$PWD\.tmp"
$env:TEMP = "$PWD\.tmp"
python -m pytest tests/ -v
```

Ket qua mong doi:

```text
3 passed
```

Anh co the chup:

- Terminal hien thi `3 passed`.
- Khong bat buoc, nhung giup chung minh code test chay duoc.

---

## 2. Task 1 - Chay MLflow experiments local

Dat bien moi truong MLflow:

```powershell
$env:MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
$env:MLFLOW_ARTIFACT_ROOT = "./mlartifacts"
$env:MLFLOW_EXPERIMENT_NAME = "day21"
```

Chay nhieu experiment voi cac tham so khac nhau:

```powershell
@'
from src.train import train

experiments = [
    {"model_type": "random_forest", "n_estimators": 50, "max_depth": 3, "min_samples_split": 2},
    {"model_type": "random_forest", "n_estimators": 100, "max_depth": 5, "min_samples_split": 2},
    {"model_type": "random_forest", "n_estimators": 200, "max_depth": 10, "min_samples_split": 5},
    {"model_type": "gradient_boosting", "n_estimators": 120, "max_depth": 3, "learning_rate": 0.08},
    {"model_type": "logistic_regression", "C": 1.0, "max_iter": 1000},
]

for params in experiments:
    acc = train(params)
    print(params, acc)
'@ | python -
```

Neu muon chay cau hinh dang de trong `params.yaml`:

```powershell
python src/train.py
```

Mo MLflow UI:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Sau do mo trinh duyet va vao:

```text
http://localhost:5000
```

Can lam tren web MLflow:

1. Chon experiment `day21`.
2. Kiem tra co it nhat 3 runs.
3. Neu cot `accuracy`, `f1_score` chua hien thi, bam nut Columns hoac icon cai dat cot de hien thi metric.
4. Sap xep theo `accuracy` giam dan.
5. Co the tick nhieu run va bam `Compare` de chup anh so sanh.

Chup anh:

```text
submission/screenshots/Task1-MlflowRun.png
```

Anh can thay:

- MLflow UI tren `localhost:5000`.
- It nhat 3 runs.
- Co metric `accuracy`, `f1_score`.
- Co params/model_type hoac cac sieu tham so khac nhau.

---

## 3. Task 1 - Cau hinh DVC voi AWS S3

### 3.1 Tao S3 bucket

Mo AWS S3 Console:

```text
https://s3.console.aws.amazon.com/s3/home
```

Tao bucket moi, vi du:

```text
day21-mlops-<ten-cua-ban>
```

Luu lai ten bucket, vi se dung trong cac lenh sau.

### 3.2 Tao AWS access key

Mo AWS IAM Console:

```text
https://console.aws.amazon.com/iam/
```

Tao IAM User hoac dung user co san. User nay can quyen doc/ghi S3 bucket.

Toi thieu can cac quyen:

```text
s3:ListBucket
s3:GetObject
s3:PutObject
s3:DeleteObject
```

Lay:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
```

Vi du region:

```text
us-east-1
```

### 3.3 Cau hinh AWS credential tren may local

Trong PowerShell:

```powershell
$env:AWS_ACCESS_KEY_ID="<AWS_ACCESS_KEY_ID>"
$env:AWS_SECRET_ACCESS_KEY="<AWS_SECRET_ACCESS_KEY>"
$env:AWS_REGION="us-east-1"
$env:BUCKET="<TEN_BUCKET_CUA_BAN>"
```

Kiem tra AWS CLI neu co cai:

```powershell
aws s3 ls
```

Neu may ban chua co AWS CLI, van co the dung DVC voi bien moi truong o tren.

### 3.4 Cau hinh DVC remote S3

Khoi tao DVC:

```powershell
dvc init -f
```

Them remote S3:

```powershell
dvc remote add -d myremote s3://$env:BUCKET/dvc
```

Neu remote da ton tai va bao loi, dung:

```powershell
dvc remote modify myremote url s3://$env:BUCKET/dvc
```

Track cac file du lieu:

```powershell
dvc add data/train_phase1.csv data/eval.csv data/train_phase2.csv
```

Push du lieu len S3:

```powershell
dvc push
```

Kiem tra:

```powershell
dvc status
```

Ket qua mong doi:

```text
Data and pipelines are up to date.
```

Mo AWS S3 Console, vao bucket cua ban, kiem tra prefix:

```text
dvc/
```

Chup anh:

```text
submission/screenshots/Task1-DVCS3.png
```

Anh can thay:

- AWS S3 bucket cua ban.
- Co folder/prefix `dvc/`.
- Ben trong co cac object DVC da push.

---

## 4. Task 2 - Tao EC2 de serve model

### 4.1 Tao EC2

Mo AWS EC2 Console:

```text
https://console.aws.amazon.com/ec2/
```

Tao instance:

- OS: Ubuntu 22.04 hoac Ubuntu 24.04.
- Instance type: `t2.micro` hoac `t3.micro`.
- Security Group:
  - Mo port `22` cho SSH.
  - Mo port `8000` cho FastAPI.
- Tai file key `.pem` ve may.

Ghi lai:

```text
EC2_PUBLIC_IP
EC2_KEY_PATH
VM_USER
```

Thong thuong Ubuntu user la:

```text
ubuntu
```

### 4.2 SSH vao EC2

Tren PowerShell:

```powershell
ssh -i "<PATH_TO_EC2_KEY.pem>" ubuntu@<EC2_PUBLIC_IP>
```

Tren EC2, cai package:

```bash
sudo apt update
sudo apt install -y python3-pip awscli
pip3 install fastapi uvicorn scikit-learn joblib boto3
mkdir -p ~/models ~/src
```

Cau hinh AWS tren EC2:

```bash
aws configure
```

Nhap:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
Default region name: us-east-1
Default output format: json
```

Thoat EC2:

```bash
exit
```

### 4.3 Copy serve.py len EC2

Tren PowerShell local:

```powershell
scp -i "<PATH_TO_EC2_KEY.pem>" src/serve.py ubuntu@<EC2_PUBLIC_IP>:~/src/serve.py
```

### 4.4 Tao systemd service tren EC2

SSH lai vao EC2:

```powershell
ssh -i "<PATH_TO_EC2_KEY.pem>" ubuntu@<EC2_PUBLIC_IP>
```

Tao service:

```bash
sudo tee /etc/systemd/system/mlops-serve.service > /dev/null <<EOF
[Unit]
Description=MLOps Model Inference Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="CLOUD_BUCKET=<TEN_BUCKET_CUA_BAN>"
Environment="AWS_DEFAULT_REGION=us-east-1"
ExecStart=/usr/bin/python3 /home/ubuntu/src/serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Reload service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mlops-serve
```

Luu y:

- Chua can start service neu model chua duoc workflow upload len S3.
- Sau khi GitHub Actions chay xong va da co `models/latest/model.pkl`, moi start/restart service.

---

## 5. Task 2 - Cau hinh GitHub Actions

Mo GitHub repo:

```text
https://github.com/edward1503/Day21-Track2-CI-CD-for-AI-Systems
```

Vao:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

Them cac secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
CLOUD_BUCKET
VM_HOST
VM_USER
VM_SSH_KEY
```

Gia tri:

- `AWS_ACCESS_KEY_ID`: access key cua IAM user.
- `AWS_SECRET_ACCESS_KEY`: secret key cua IAM user.
- `AWS_REGION`: vi du `us-east-1`.
- `CLOUD_BUCKET`: ten S3 bucket.
- `VM_HOST`: public IP cua EC2.
- `VM_USER`: thuong la `ubuntu`.
- `VM_SSH_KEY`: toan bo noi dung private key dung SSH vao EC2.

Lay `VM_SSH_KEY` tren Windows:

```powershell
Get-Content "<PATH_TO_EC2_KEY.pem>" -Raw
```

Copy toan bo output, bao gom:

```text
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```

Hoac:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

---

## 6. Task 2 - Push code va xem pipeline

Truoc khi commit, kiem tra:

```powershell
git status
```

Add cac file can thiet:

```powershell
git add .dvc .dvcignore .gitignore data/*.dvc .github/workflows/mlops.yml params.yaml requirements.txt src tests LAB_REPORT.md SUBMISSION_COMMANDS.md submission
```

Commit:

```powershell
git commit -m "feat: complete mlops ci cd pipeline"
```

Push:

```powershell
git push origin main
```

Neu branch cua ban la `master`:

```powershell
git push origin master
```

Mo GitHub Actions:

```text
GitHub repo -> Actions -> MLOps Pipeline -> workflow run moi nhat
```

Theo doi 4 jobs:

```text
Unit Test
Train
Eval
Deploy
```

Chup anh:

```text
submission/screenshots/Task2-GithubActionsFlow.png
```

Anh can thay:

- Workflow run moi nhat.
- 4 jobs deu mau xanh.

Chup log Eval:

```text
submission/screenshots/Task2-CheckEvalGate.png
```

Anh can thay:

- Job `Eval`.
- Dong log co accuracy.
- Dong `PASSED: accuracy ... >= 0.70` hoac neu muon minh chung gate fail thi co dong `FAILED: accuracy ... < 0.70`.

---

## 7. Task 2 - Test API tren EC2

Sau khi workflow Deploy thanh cong, SSH vao EC2 va kiem tra service:

```powershell
ssh -i "<PATH_TO_EC2_KEY.pem>" ubuntu@<EC2_PUBLIC_IP>
```

Tren EC2:

```bash
sudo systemctl status mlops-serve
sudo journalctl -u mlops-serve -n 50 --no-pager
```

Neu service chua chay:

```bash
sudo systemctl start mlops-serve
```

Thoat EC2:

```bash
exit
```

Test tu may local:

```powershell
$env:VM_IP="<EC2_PUBLIC_IP>"
curl http://$env:VM_IP:8000/health
```

Ket qua mong doi:

```json
{"status":"ok"}
```

Test predict:

```powershell
curl -X POST http://$env:VM_IP:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"features": [7.4, 0.70, 0.00, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4, 0]}'
```

Ket qua mong doi:

```json
{"prediction":0,"label":"thap"}
```

Hoac prediction co the khac tuy model, nhung phai tra ve JSON co:

```text
prediction
label
```

Chup anh:

```text
submission/screenshots/Task2-EC2Curl.png
```

Anh can thay:

- Lenh curl `/health`.
- Lenh curl `/predict`.
- Output JSON tra ve.

---

## 8. Task 3 - Continuous training khi co du lieu moi

Them du lieu phase 2 vao train phase 1:

```powershell
python add_new_data.py
```

Ket qua mong doi:

```text
Cap nhat du lieu: 2998 -> 5996 mau
```

Kiem tra so dong:

```powershell
(Get-Content data\train_phase1.csv).Count
```

Ket qua mong doi:

```text
5997
```

Cap nhat DVC pointer:

```powershell
dvc add data/train_phase1.csv
```

Push du lieu moi len S3 truoc:

```powershell
dvc push
```

Commit file `.dvc`, khong commit file CSV:

```powershell
git add data/train_phase1.csv.dvc
git commit -m "data: add train phase 2 samples"
git push origin main
```

Neu branch la `master`:

```powershell
git push origin master
```

Mo GitHub Actions:

```text
GitHub repo -> Actions -> MLOps Pipeline
```

Tim workflow run duoc kich hoat boi commit:

```text
data: add train phase 2 samples
```

Chup anh:

```text
submission/screenshots/Task3-NewActions.png
```

Anh can thay:

- Workflow run cua commit data.
- 4 jobs xanh.

Chup log Eval:

```text
submission/screenshots/Task3-EvalGatePass.png
```

Anh can thay:

- Accuracy moi.
- Dong `PASSED`.
- Neu dung cau hinh hien tai, local da kiem tra accuracy khoang `0.7660`.

Test lai API sau deploy:

```powershell
curl http://$env:VM_IP:8000/health
curl -X POST http://$env:VM_IP:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"features": [7.4, 0.70, 0.00, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4, 0]}'
```

---

## 9. Bonus - Can chup gi

### Bonus 1 - MLflow tu xa voi DagsHub

Mo DagsHub:

```text
https://dagshub.com
```

Tao repo/link voi GitHub repo cua ban, lay MLflow tracking URI.

Them GitHub Secrets:

```text
MLFLOW_TRACKING_URI
MLFLOW_TRACKING_USERNAME
MLFLOW_TRACKING_PASSWORD
```

Chay GitHub Actions lai.

Chup anh:

```text
submission/screenshots/BONUS-1.png
```

Anh can thay:

- DagsHub MLflow UI.
- Co runs duoc log tu workflow.

### Bonus 2 - Nhieu thuat toan

Mo MLflow UI local hoac DagsHub MLflow.

Chup anh:

```text
submission/screenshots/BONUS-2.png
```

Anh can thay:

- Cac run co `model_type` khac nhau:
  - `random_forest`
  - `gradient_boosting`
  - `logistic_regression`
  - hoac `extra_trees`

### Bonus 3 - Bao cao tu dong

Mo GitHub Actions run:

```text
Actions -> workflow run -> Artifacts -> training-report
```

Tai artifact hoac mo log upload artifact.

Chup anh:

```text
submission/screenshots/BONUS-3.png
```

Anh can thay:

- Artifact `training-report`.
- Co `metrics.json`.
- Co `report.txt`.

### Bonus 4 - Rollback guard

Mo log job `Train`, step:

```text
Compare with previous deployed model
```

Chup anh:

```text
submission/screenshots/BONUS-4.png
```

Anh can thay mot trong cac dong:

```text
Previous deployed accuracy
New candidate accuracy
PASSED: new model is at least as accurate as the deployed model
```

Hoac neu model moi kem hon:

```text
FAILED: new accuracy ... < previous accuracy ...
```

### Bonus 5 - Data drift / label distribution

Mo log job `Train`, step `Train model`, hoac mo artifact `metrics.json`.

Chup anh:

```text
submission/screenshots/BONUS-5.png
```

Anh can thay:

- `train_label_distribution`
- Hoac log:

```text
Train label distribution
DATA DRIFT WARNING
```

Neu khong co warning thi van hop ly, vi du lieu hien tai moi class deu tren 10%.

---

## 10. Checklist anh nop bai

Bat buoc nen co:

```text
submission/screenshots/Task1-MlflowRun.png
submission/screenshots/Task1-DVCS3.png
submission/screenshots/Task2-GithubActionsFlow.png
submission/screenshots/Task2-CheckEvalGate.png
submission/screenshots/Task2-EC2Curl.png
submission/screenshots/Task3-NewActions.png
submission/screenshots/Task3-EvalGatePass.png
```

Neu lam bonus:

```text
submission/screenshots/BONUS-1.png
submission/screenshots/BONUS-2.png
submission/screenshots/BONUS-3.png
submission/screenshots/BONUS-4.png
submission/screenshots/BONUS-5.png
```

---

## 11. Checklist truoc khi nop

Kiem tra git:

```powershell
git status
```

Kiem tra remote:

```powershell
git remote -v
```

Kiem tra DVC:

```powershell
dvc status
```

Kiem tra test:

```powershell
mkdir .tmp -ErrorAction SilentlyContinue
$env:TMP = "$PWD\.tmp"
$env:TEMP = "$PWD\.tmp"
python -m pytest tests/ -v
```

Kiem tra train:

```powershell
python src/train.py
Get-Content outputs\metrics.json
Get-Content outputs\report.txt
```

Nop:

1. Link GitHub repo public.
2. Anh trong `submission/screenshots/`.
3. File report ngan, co the dung `LAB_REPORT.md`.

Khong nop anh duoc tao bang script.
