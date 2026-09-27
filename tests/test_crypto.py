import unittest

from steganography.crypto import decrypt_message, encrypt_message


class TestCrypto(unittest.TestCase):
    def test_encrypt_decrypt(self):
        message = "Pesan rahasia untuk pengujian."
        key = "Rafli123"
        ciphertext = encrypt_message(message, key)
        self.assertNotEqual(ciphertext, message.encode("utf-8"))
        self.assertEqual(decrypt_message(ciphertext, key), message)


if __name__ == "__main__":
    unittest.main()
