from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def _array(image):
    return np.asarray(image.convert("RGB"), dtype=np.float64)


def calculate_mse(original: Image.Image, modified: Image.Image) -> float:
    a = _array(original)
    b = _array(modified)

    if a.shape != b.shape:
        raise ValueError("Images must have the same dimensions.")

    return float(np.mean((a - b) ** 2))


def calculate_psnr(original: Image.Image, modified: Image.Image) -> float:
    mse = calculate_mse(original, modified)
    if mse == 0:
        return float("inf")
    max_pixel = 255.0
    return float(10 * np.log10((max_pixel ** 2) / mse))


def save_histogram(
    cover: Image.Image,
    stego: Image.Image,
    output_path: str,
):
    cover_arr = np.asarray(cover.convert("RGB"))
    stego_arr = np.asarray(stego.convert("RGB"))

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    for channel, name in enumerate(("Red", "Green", "Blue")):
        axes[0].hist(
            cover_arr[:, :, channel].ravel(),
            bins=256,
            alpha=0.45,
            label=f"Cover {name}",
        )
        axes[0].hist(
            stego_arr[:, :, channel].ravel(),
            bins=256,
            alpha=0.45,
            label=f"Stego {name}",
        )

    axes[0].set_title("Histogram Comparison")
    axes[0].set_xlabel("Pixel Value")
    axes[0].set_ylabel("Frequency")
    axes[0].legend()

    for channel, name in enumerate(("Red", "Green", "Blue")):
        axes[1].plot(
            np.bincount(cover_arr[:, :, channel].ravel(), minlength=256),
            label=f"Cover {name}",
        )
        axes[1].plot(
            np.bincount(stego_arr[:, :, channel].ravel(), minlength=256),
            label=f"Stego {name}",
        )

    axes[1].set_title("Histogram Frequency Curves")
    axes[1].set_xlabel("Pixel Value")
    axes[1].set_ylabel("Frequency")
    axes[1].legend()

    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
