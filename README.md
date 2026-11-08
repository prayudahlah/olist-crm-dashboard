# CRM Dashboard, Olist

Tugas Business Intelligence. Dashboard CRM untuk perusahaan retail, memakai dataset
[Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Struktur

| Path | Isi |
|---|---|
| `01_olist_crm.ipynb` | pipeline dan analisis, sumber kebenaran semua angka |
| `app.py` | dashboard Streamlit, tiga halaman, hanya baca schema `marts` |
| `olist.duckdb` | hasil olahan, dibuat ulang oleh notebook |
| `data/raw/olist/` | CSV mentah, tidak ikut di-commit |
| `figures/` | gambar dari notebook |

## Menjalankan

Jalankan dari folder proyek:

```fish
uv sync
uv run streamlit run app.py
```

Membuka ulang notebook:

```fish
uv run jupyter lab 01_olist_crm.ipynb
```

Membangun ulang database dari CSV, jalankan notebook dari atas ke bawah. Notebook
menimpa `olist.duckdb` dan semua tabel di schema `marts`.

## Halaman

1. **Ringkasan**, GMV, order, AOV, pelanggan, repeat rate, tren bulanan, performa
   state, dan kategori terbesar. Ada filter state, kategori, dan tahun.
2. **Pelanggan**, segmen RFM, pelanggan dengan nilai terbesar, dan daftar berisiko
   yang bisa diunduh.
3. **Strategi**, ranking kategori menurut repeat rate, repeat menurut rating dan
   ketepatan kirim, prioritas wilayah, serta rencana aksi per segmen.

## Definisi metrik

- GMV, jumlah `payment_total` pada order non-canceled, periode Januari 2017 sampai Agustus 2018
- Repeat rate, pelanggan dengan minimal dua order dibagi total pelanggan
- RFM, R pita hari mengikuti ambang churn, F jumlah order, M quintile belanja
- At-risk, lebih dari 90 hari tanpa order, yaitu `greatest(2 x median gap, 90 hari)`
- Retensi cohort, pelanggan yang kembali pada bulan ke-n dibagi ukuran cohort pertama

## Catatan

- Pelanggan dihitung dengan `customer_unique_id`, bukan `customer_id`.
- Ambang churn memakai tanggal acuan dari data, bukan tanggal hari ini.
- File review punya 10 baris rusak yang dilewati saat parsing.
