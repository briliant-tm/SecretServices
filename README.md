# Secure Image Steganography - LSB

Aplikasi desktop Python untuk menyisipkan dan mengekstraksi pesan teks pada citra PNG/BMP menggunakan metode Least Significant Bit (LSB), XOR encryption, dan randomisasi posisi channel berdasarkan stego-key.

## 1. Fitur

- Embed pesan teks ke citra PNG/BMP.
- Extract pesan dari citra stego.
- Enkripsi pesan dengan XOR menggunakan key hasil SHA-256.
- Randomisasi posisi channel RGB menggunakan PRNG berbasis stego-key.
- Header magic, version, dan panjang payload.
- Perhitungan kapasitas maksimum.
- Validasi pesan yang melebihi kapasitas.
- Perhitungan MSE dan PSNR.
- Visualisasi enhanced LSB.
- Perbandingan histogram cover dan stego.
- Pengujian unit untuk fungsi inti.

## 2. Persyaratan

Python 3.10 atau lebih baru disarankan.

## 3. Instalasi

Buka terminal di folder proyek:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

## 4. Menjalankan aplikasi

```bash
python app.py
```

## 5. Cara menggunakan Embed

1. Buka tab `Embed Message`.
2. Pilih gambar PNG/BMP.
3. Masukkan pesan.
4. Masukkan stego-key.
5. Klik `EMBED MESSAGE`.
6. Simpan hasil sebagai PNG atau BMP.
7. Aplikasi menampilkan MSE dan PSNR.

## 6. Cara menggunakan Extract

1. Buka tab `Extract Message`.
2. Pilih gambar stego PNG/BMP.
3. Masukkan stego-key yang sama.
4. Klik `EXTRACT MESSAGE`.
5. Pesan akan ditampilkan jika key dan data benar.

## 7. Enhanced LSB

Masuk ke tab `Analysis`, lalu pilih `Choose PNG/BMP Image`. Aplikasi akan membuat visualisasi bidang LSB yang dapat disimpan sebagai PNG.

## 8. Histogram

Setelah proses embed berhasil, masuk ke tab `Analysis` dan pilih `Save Histogram of Cover/Stego`.

## 9. Menjalankan Unit Test

Dari root project:

```bash
python -m unittest discover -s tests -v
```

Target awal:

```text
Ran 6 tests
OK
```

## 10. Catatan Pengujian UTS

Untuk pengujian utama gunakan PNG/BMP. Jangan mengubah stego image menjadi JPEG sebelum proses extraction karena kompresi JPEG bersifat lossy dan dapat merusak data LSB.

Pengujian JPEG tetap dilakukan sebagai uji kerapuhan: simpan stego image sebagai JPEG lalu coba ekstraksi dan dokumentasikan hasilnya.

## 11. Struktur

```text
secure-steganography/
├── app.py
├── steganography/
│   ├── __init__.py
│   ├── crypto.py
│   ├── lsb.py
│   └── metrics.py
├── utils/
├── tests/
├── assets/
├── testing/
├── requirements.txt
└── README.md
```

## 12. Catatan Keamanan

Proyek ini dibuat untuk kebutuhan pembelajaran steganografi. XOR digunakan sebagai enkripsi sederhana sesuai ruang lingkup tugas. Untuk sistem produksi, gunakan algoritma kriptografi modern yang memiliki autentikasi/integritas, seperti AES-GCM.

Jangan memasukkan data pribadi atau rahasia nyata ke dalam repository GitHub.
