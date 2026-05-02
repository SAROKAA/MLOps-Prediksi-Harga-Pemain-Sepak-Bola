# ⚽ MLOps: Prediksi Harga Pemain Sepak Bola

Proyek ini adalah implementasi **MLOps Pipeline** untuk memprediksi nilai pasar (_Market Value_) pemain sepak bola berdasarkan performa statistik historis. Sistem ini mengintegrasikan alur penyerapan data otomatis, pemrosesan fitur (Feature Engineering), dan kontrol versi data (**DVC**) untuk mendukung pengembangan model yang berkelanjutan (_Continual Learning_).

## 🎯 Tujuan Proyek

- Membangun pipeline data otomatis yang mengambil data dari berbagai endpoint API (Statistik & Transfer).
- Melakukan **Data Fusion** untuk menyatukan performa teknis dengan nilai ekonomi pemain.
- Mengimplementasikan **Data Version Control (DVC)** untuk melacak siklus hidup dataset tanpa membebani repositori Git.
- Mendukung mekanisme _Continuous Training_ dengan dataset yang ter-versioning dengan baik.

---

## 📂 Struktur Direktori

```text
MLOps-Prediksi-Harga-Pemain-Sepak-Bola/
├── data/
│   ├── raw/                  # Landing Zone (Data Mentah JSON)
│   │   ├── league_621/       # Statistik pemain per tim
│   │   └── transfers/        # Riwayat transfer per pemain (per tim)
│   └── processed/            # Silver/Gold Zone (Data Master CSV)
│       └── data_processed_YYYYMMDD_HHMMSS.csv
├── src/
│   ├── data/                 # Modul Data Engineering
│   │   ├── ingest_data.py             # Ingest statistik liga
│   │   ├── ingest_transfers_per_team.py # Ingest harga transfer per tim
│   │   └── preprocess.py    # Cleaning, Join, & Feature Engineering
├── .dvc/                     # Konfigurasi Internal DVC
├── requirements.txt          # Daftar Library Python
└── README.md                 # Dokumentasi Proyek
🛠️ Panduan Menjalankan Pipeline
1. Ingest Data (Data Acquisition)
Pastikan API Key sudah terpasang di file .env. Jalankan script untuk mengambil data statistik liga dan riwayat transfer secara bertahap (Batching):

Bash
# Ambil statistik dasar tim
python src/data/ingest_data.py

# Ambil data transfer (Contoh: Manchester City)
# Ubah variabel tim_target di dalam script untuk tim lainnya
python src/data/ingest_transfers_per_team.py
2. Preprocessing & Data Fusion
Script ini akan menggabungkan semua file JSON di folder raw, membersihkan simbol mata uang (misal: € 74M → 74000000.0), dan menghasilkan satu file Master CSV di folder processed:

Bash
python src/data/preprocess_all_teams.py
🔄 Data Versioning (DVC)
Sesuai prinsip Analitik Big Data (ABD03), kami menggunakan DVC untuk menjamin Veracity dan Traceability dataset.

Inisialisasi & Tracking Awal
Bash
# Inisialisasi DVC di project
dvc init

# Mulai melacak dataset master
dvc add data/processed/master_processed_TIMESTAMP.csv

# Daftarkan metadata ke Git
git add data/processed/master_processed_TIMESTAMP.csv.dvc data/processed/.gitignore
git commit -m "Track initial dataset version (v1)"
Simulasi Continual Learning (Update Data)
Setiap kali ada penambahan data pemain baru atau tim baru:

Jalankan kembali pipeline preprocessing untuk memperbarui Master CSV.

Gunakan perintah audit untuk melihat perbedaan:

Bash
dvc status   # Cek file yang berubah
dvc diff     # Lihat perubahan Hash MD5 (Audit silsilah data)
Update versi dataset di DVC:

Bash
dvc add data/processed/master_processed_TIMESTAMP.csv
git add data/processed/master_processed_TIMESTAMP.csv.dvc
git commit -m "Update dataset: Penambahan data tim baru (v2)"
📈 Metodologi Sains Data (ABD03)
Implementasi pipeline ini mengikuti siklus hidup data:

Discovery: Identifikasi player_id yang konsisten untuk menghubungkan data statistik dan data transfer.

Data Preparation: Penanganan Variety data (konversi string ke float) dan eliminasi noise (pemain tanpa menit bermain).

Data Fusion: Integrasi data performa (Features) dan harga pasar (Label) melalui teknik mapping berbasis ID unik.

Data Versioning: Penggunaan Hash MD5 untuk menjamin integritas data di setiap iterasi model.

💻 Cara Menjalankan di Codespaces
Buka repositori di GitHub, pilih Code > Codespaces > Create Codespace.

Install semua dependency:

Bash
pip install -r requirements.txt
```
