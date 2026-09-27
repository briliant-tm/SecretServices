import unittest

from PIL import Image

from steganography.lsb import (
    calculate_capacity_bytes,
    embed_message,
    extract_message,
)


class TestLSB(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGB", (200, 200), (120, 150, 180))

    def test_capacity_positive(self):
        self.assertGreater(calculate_capacity_bytes(self.image), 0)

    def test_embed_extract(self):
        message = "Halo, ini pesan rahasia."
        key = "Rafli123"
        stego = embed_message(self.image, message, key)
        self.assertEqual(extract_message(stego, key), message)

    def test_wrong_key_fails(self):
        message = "Pesan rahasia."
        stego = embed_message(self.image, message, "benar")
        with self.assertRaises(ValueError):
            extract_message(stego, "salah")

    def test_oversized_message_rejected(self):
        tiny = Image.new("RGB", (10, 10), (100, 100, 100))
        message = "X" * 1000
        with self.assertRaises(ValueError):
            embed_message(tiny, message, "key")


if __name__ == "__main__":
    unittest.main()
