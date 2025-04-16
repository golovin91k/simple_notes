import base64
import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


key = os.urandom(16)
iv = os.urandom(16)


def encryption(token):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_token = cipher.encrypt(pad(token.encode(), AES.block_size))
    encoded_encrypted_token = base64.urlsafe_b64encode(
        encrypted_token).decode('utf-8')
    return encoded_encrypted_token


def decryption(token):
    decoded_encrypted_token = base64.urlsafe_b64decode(token.encode('utf-8'))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_token = unpad(
        cipher.decrypt(decoded_encrypted_token), AES.block_size)

    try:
        decrypted_token_str = decrypted_token.decode('utf-8')

    except UnicodeDecodeError:
        decrypted_token_str = decrypted_token

    return decrypted_token_str
