import csv
import time
from pathlib import Path

from PIL import Image

from steganography.lsb import embed_message, extract_message, calculate_capacity_bytes
from steganography.metrics import mse, psnr

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "testing" / "images"
RESULT_DIR = ROOT / "testing" / "results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

TESTS = [
    ("kecil", 100),
    ("sedang", 1024),
    ("besar", 5120),
]

KEY = "UTS-Stego-2026-Key"


def make_message(size):
    pattern = "Pesan pengujian steganografi UTS Information Security. "
    raw = (pattern * ((size // len(pattern)) + 1)).encode("utf-8")
    return raw[:size].decode("utf-8", errors="ignore")


def main():
    images = sorted(
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in {".png", ".bmp"}
    )

    if len(images) < 5:
        print(f"ERROR: ditemukan {len(images)} gambar. Minimal 5 PNG/BMP diperlukan.")
        return

    rows = []

    for image_path in images[:5]:
        cover = Image.open(image_path).convert("RGB")
        capacity = calculate_capacity_bytes(cover)

        for label, requested_size in TESTS:
            message = make_message(requested_size)
            actual_size = len(message.encode("utf-8"))

            row = {
                "gambar": image_path.name,
                "ukuran_pesan": label,
                "target_byte": requested_size,
                "actual_byte": actual_size,
                "kapasitas_byte": capacity,
                "status_embed": "Gagal",
                "mse": "",
                "psnr_db": "",
                "status_extract": "Gagal",
                "pesan_sesuai": "Tidak",
                "waktu_ms": "",
                "catatan": "",
            }

            try:
                if actual_size > capacity:
                    raise ValueError(
                        f"Pesan {actual_size} byte melebihi kapasitas {capacity} byte."
                    )

                start = time.perf_counter()
                stego = embed_message(cover, message, KEY)
                row["waktu_ms"] = round(
                    (time.perf_counter() - start) * 1000, 4
                )

                output_path = RESULT_DIR / f"{image_path.stem}_{label}_stego.png"
                stego.save(output_path, format="PNG")

                row["status_embed"] = "Berhasil"
                row["mse"] = round(mse(cover, stego), 8)
                row["psnr_db"] = round(psnr(cover, stego), 4)

                extracted = extract_message(stego, KEY)
                row["status_extract"] = "Berhasil"
                row["pesan_sesuai"] = (
                    "Ya" if extracted == message else "Tidak"
                )

            except Exception as exc:
                row["catatan"] = str(exc).replace("\n", " ")

            rows.append(row)

            print(
                f"{image_path.name:25} | {label:6} | "
                f"embed={row['status_embed']:8} | "
                f"extract={row['status_extract']:8} | "
                f"PSNR={row['psnr_db']}"
            )

    csv_path = RESULT_DIR / "hasil_pengujian_15.csv"

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("\nSELESAI")
    print(f"Hasil: {csv_path}")


if __name__ == "__main__":
    main()
