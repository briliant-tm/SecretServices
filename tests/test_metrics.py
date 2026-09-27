import unittest

from PIL import Image

from steganography.metrics import calculate_mse, calculate_psnr


class TestMetrics(unittest.TestCase):
    def test_identical_images(self):
        image = Image.new("RGB", (10, 10), (10, 20, 30))
        self.assertEqual(calculate_mse(image, image), 0.0)
        self.assertEqual(calculate_psnr(image, image), float("inf"))


if __name__ == "__main__":
    unittest.main()
