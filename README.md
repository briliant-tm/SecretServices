# Secret Services

Aplikasi steganografi citra berbasis LSB (Least Significant Bit) untuk menyembunyikan pesan rahasia ke dalam file gambar tanpa mengubah tampilan visual secara signifikan. Proyek ini juga dilengkapi dengan enkripsi XOR, kunci stego, serta analisis kualitas citra seperti MSE dan PSNR.

## Deskripsi Proyek

Secret Services merupakan proyek untuk kebutuhan keamanan informasi yang fokus pada:

- Penyisipan pesan rahasia ke dalam gambar menggunakan teknik LSB
- Enkripsi pesan sebelum disisipkan menggunakan XOR dengan kunci yang diturunkan dari stego-key
- Ekstraksi pesan dari citra stego dengan verifikasi kunci
- Analisis kualitas citra hasil penyisipan
- Antarmuka GUI untuk penggunaan yang mudah

Proyek ini dibuat sebagai implementasi praktis dari konsep steganografi digital dan keamanan media penyimpanan gambar.

## Fitur Utama

- LSB embedding pada channel RGB image
- Stego-key untuk menjaga keamanan proses embedding dan extraction
- Header metadata yang berisi magic number, versi format, dan panjang payload
- Validasi kapasitas pesan sebelum penyisipan
- Visualisasi LSB plane dari citra
- Pengukuran kualitas:
  - MSE (Mean Squared Error)
  - PSNR (Peak Signal-to-Noise Ratio)
  - histogram perbandingan citra cover dan stego
- GUI berbasis Tkinter

## Teknologi yang Digunakan

- Python 3
- Pillow (PIL)
- NumPy
- Matplotlib
- Tkinter (standar library Python)

## Struktur Proyek

```text
SecretServices/
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_INFO.txt
├── steganography/
│   ├── __init__.py
│   ├── crypto.py
│   ├── lsb.py
│   └── metrics.py
├── tests/
│   ├── __init__.py
│   ├── run_batch_test.py
│   ├── test_crypto.py
│   ├── test_lsb.py
│   └── test_metrics.py
├── Testing/
│   ├── message_besar.txt
│   ├── message_kecil.txt
│   ├── message_sedang.txt
│   └── Image/
│       └── Result/
└── utils/
    └── __init__.py
```

## Persyaratan Sistem

Pastikan Anda sudah memiliki:

- Python 3.9 atau lebih tinggi
- pip
- library berikut: Pillow, NumPy, Matplotlib

Install dependensi dengan perintah:

```bash
pip install -r requirements.txt
```

## Cara Menjalankan

Jalankan aplikasi GUI:

```bash
python app.py
```

Setelah aplikasi terbuka, Anda dapat:

1. Memilih gambar cover
2. Menulis pesan yang akan disembunyikan
3. Mengisi stego-key
4. Menekan tombol embed untuk menghasilkan citra stego
5. Menggunakan fitur extract untuk membaca pesan kembali
6. Menjalankan analisis kualitas gambar untuk melihat MSE, PSNR, dan histogram

## Alur Kerja Aplikasi

### 1. Embedding

- Gambar cover dibaca
- Pesan dikonversi ke bentuk bytes
- Pesan dienkripsi dengan XOR dan kunci stego
- Header metadata ditambahkan
- Bit-bit payload disisipkan ke LSB channel RGB sesuai urutan posisi yang diacak berdasarkan stego-key
- Hasilnya adalah citra stego

### 2. Extraction

- Citra stego dibaca
- Posisi channel diacak kembali menggunakan stego-key yang sama
- Header diekstraksi untuk mengetahui panjang payload
- Pesan terenkripsi dibaca dan didekripsi
- Pesan asli dikembalikan dalam bentuk string

### 3. Analysis

Fungsi analisis menghitung:

- MSE = rata-rata selisih kuadrat antara piksel cover dan stego
- PSNR = kualitas sinyal terhadap noise pada citra
- Histogram = perbandingan distribusi intensitas piksel cover dan stego

## Modul Utama

### steganography/lsb.py

Berisi logika inti steganografi:

- `calculate_capacity_bytes()`
- `embed_message()`
- `extract_message()`
- `visualize_lsb()`

### steganography/crypto.py

Menyediakan fungsi enkripsi dan dekripsi:

- `derive_key()`
- `xor_bytes()`
- `encrypt_message()`
- `decrypt_message()`

### steganography/metrics.py

Menangani evaluasi kualitas gambar:

- `calculate_mse()`
- `calculate_psnr()`
- `save_histogram()`

## Pengujian

Untuk menjalankan unit test:

```bash
python -m unittest discover -s tests -v
```

Test yang tersedia mencakup:

- validasi kapasitas citra
- embed dan extract pesan
- pengecekan pesan dengan kunci yang salah
- pembatasan ukuran pesan yang terlalu besar
- validasi fungsi enkripsi/dekripsi
- pengecekan MSE dan PSNR

## Catatan Keamanan

- Gunakan stego-key yang kuat dan tidak mudah ditebak
- Pastikan kunci yang digunakan saat embed dan extract sama
- Jika kunci salah, pesan yang diekstraksi tidak akan valid atau akan menimbulkan error
- Teknik LSB tidak sepenuhnya aman dari analisis steganalisis yang lebih canggih, namun untuk keperluan pembelajaran dan prototipe ini sudah cukup representatif

## Lisensi

Proyek ini dibuat untuk kebutuhan akademik dan pembelajaran keamanan informasi. Silakan sesuaikan lisensi sesuai kebutuhan penggunaan Anda.

## Penutup

Secret Services adalah proyek yang menampilkan bagaimana pesan dapat disembunyikan dalam citra digital menggunakan teknik LSB dengan pendekatan keamanan tambahan melalui enkripsi dan kunci stego. Proyek ini cocok untuk pembelajaran, demo, dan pengembangan lebih lanjut dalam bidang steganografi digital.
