# MLOps Prediksi Harga Pemain Sepak Bola

## Tujuan Proyek

Proyek ini bertujuan untuk membangun sistem prediksi nilai pasar pemain sepak bola menggunakan pendekatan Machine Learning berbasis Time Series dengan implementasi MLOps pipeline.

Sistem dirancang untuk menangani perubahan performa pemain yang dinamis melalui mekanisme continuous training, sehingga model dapat diperbarui secara berkala ketika data statistik pemain terbaru tersedia.

Dengan pendekatan ini, sistem dapat membantu dalam melakukan estimasi nilai pasar pemain secara lebih akurat berdasarkan data performa historis.

---

## Struktur Direktori

Berikut struktur proyek yang digunakan:

```
MLOps-Prediksi-Harga-Pemain-Sepak-Bola/
│
├── data/           → Berkaitan dengan data yang digunakan dalam proyek
│   ├── raw/        → Data mentah yang diperoleh dari sumber data
│   └── processed/  → Data yang telah melalui tahap preprocessing
│
├── models/         → Penyimpanan model hasil training
├── notebooks/      → Eksperimen dan Exploratory Data Analysis (EDA)
├── src/            → Source code utama (data ingestion, training, dll)
├── config/         → File konfigurasi (parameter model, setting pipeline)
├── tests/          → Unit testing
├── docs/           → Dokumentasi tambahan
│
├── requirements.txt
└── README.md
```
---

## Cara Menjalankan Project di Codespaces

1. Buka repository di GitHub
2. Klik tombol **Code**
3. Pilih tab **Codespaces**
4. Klik **Create Codespace**
5. Tunggu environment selesai loading
6. Install dependency dengan:

```
pip install -r requirements.txt
```

7. Jalankan script Python sesuai kebutuhan, misalnya:

```
python src/hello.py
```

---

## Workflow Git

Project ini menggunakan GitHub Flow:

- Buat branch fitur dari `main`
- Lakukan commit di branch fitur
- Buat Pull Request
- Merge ke `main` setelah divalidasi