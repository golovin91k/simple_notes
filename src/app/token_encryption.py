import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Генерация ключа и инициализационного вектора (IV)
key = os.urandom(16)  # Ключ для AES (16 байт для AES-128)
iv = os.urandom(16)   # Инициализационный вектор


def encryption(token):
    # Преобразуем строку в байты и шифруем
    print(key)
    print('________________________')
    print(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_token = cipher.encrypt(pad(token.encode(), AES.block_size))

    # Кодируем результат в base64 для безопасной передачи
    encoded_encrypted_token = base64.urlsafe_b64encode(encrypted_token).decode('utf-8')

    return encoded_encrypted_token


def decryption(token):
    # Декодируем base64
    decoded_encrypted_token = base64.urlsafe_b64decode(token.encode('utf-8'))

    # Дешифруем
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_token = unpad(cipher.decrypt(decoded_encrypted_token), AES.block_size)

    try:
        # Преобразуем байты обратно в строку
        decrypted_token_str = decrypted_token.decode('utf-8')

    except UnicodeDecodeError:
        # Если данные не могут быть декодированы как UTF-8, это бинарные данные или другие форматы
        decrypted_token_str = decrypted_token  # Возвращаем как байты
        print('ne poluchilos')
    return decrypted_token_str


asd = '1'

enc_asd = encryption(asd)
decr_asd = decryption(enc_asd)

print(enc_asd)

print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

print(decr_asd)

