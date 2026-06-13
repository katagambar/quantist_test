# Data Ingestion Pipeline untuk Quantist.io

Folder `pipeline` ini berisi skrip-skrip untuk mengambil data dari berbagai sumber (Bursa Efek, Yahoo Finance, dll) dan memasukkannya ke dalam tabel PostgreSQL/Supabase yang digunakan oleh web app Quantist.io.

## Persiapan
Script ini membutuhkan akses ke database Supabase yang sama. Pastikan environment variable `DATABASE_URL` sudah tersetting.

## Menjalankan Scraper Yahoo Finance (Data Harga Historis)
Skrip `scraper.py` menggunakan `yfinance` untuk menarik data OHLCV.

```bash
pip install yfinance pandas sqlalchemy psycopg-binary
python pipeline/scraper.py
```

*Catatan: Yahoo Finance hanya menyediakan harga dan volume (OHLCV). Untuk analisis Whale Flow (Foreign Flow / Broker Summary), Anda membutuhkan data spesifik BEI (seperti Data Broker dan Transaksi Asing).*

## Cara Mendapatkan Data Broker Summary & Foreign Flow
Aplikasi Quantist.io sangat bergantung pada tabel `stocktransaction` (Data broker buy/sell) dan kolom `foreignbuy`/`foreignsell` di `stockdata`.

Karena data tersebut berbayar atau tertutup, skrip `scraper.py` yang disediakan di sini hanya sebagai **kerangka/pondasi awal** (mengisi 0 pada data foreign/broker).

Anda bisa memperluas skrip ini dengan menghubungkannya ke API sekuritas berbayar atau layanan API lokal Indonesia (seperti goapi.id) untuk mengisi tabel-tabel tersebut.
