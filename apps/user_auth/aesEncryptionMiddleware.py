from Crypto.Cipher import AES
import base64
from django.utils.deprecation import MiddlewareMixin
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from django.conf import settings

# def encrypt_aes(plain_text, key):
#     try:
#         cipher = AES.new(key, AES.MODE_ECB)
#         padding_length = 16 - (len(plain_text) % 16)
#         padded_plain_text = plain_text + (chr(padding_length) * padding_length)
#         encrypted_data = cipher.encrypt(padded_plain_text.encode('utf-8'))
#         return base64.b64encode(encrypted_data).decode('utf-8')
#     except Exception as e:
#         print("Encryption error:", e)
#         return None
    
# def decrypt_aes(encrypted_data, key):
#     try:
#         cipher = AES.new(key, AES.MODE_ECB)
#         decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
#         padding_length = decrypted_data[-1]
#         decrypted_data = decrypted_data[:-padding_length]
#         return decrypted_data.decode('utf-8')
#     except Exception as e:
#         print("Decryption error:", e)
#         return None


# class AesEncryptionMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.secret_key = b'secret_key_here'
#         self.initialization_vector = b'initialization_vector_here'

#     def __call__(self, request):
#         if request.method in ['POST', 'PUT', 'PATCH'] and request.body:
#             try:
#                 key = base64.b64decode("bXVzdGJlMTZieXRlc2tleQ==")
#                 data = json.loads(request.body)
#                 print('data: >>>>>>>>>>>>>>>>>>>>.', data)
#                 decrypt_body = decrypt_aes(data, key)
#                 request._body = decrypt_body.encode('utf-8')
#             except Exception as e:
#                 print("Decryption failed:", e)

#         response = self.get_response(request)

#         if response['Content-Type'] == 'application/json':
#             try:
#                 data = json.loads(response.content.decode('utf-8'))
#                 print('data: ', data)
#                 key = base64.b64decode("bXVzdGJlMTZieXRlc2tleQ==")
#                 encrypt_data = encrypt_aes(json.dumps(data), key)
#                 print('encrypt_data: ', encrypt_data)
#                 response.content = json.dumps(encrypt_data)
#                 # response.content = json.dumps(encrypt_data)
#             except Exception as e:
#                 print("Encryption failed:", e)

        
#         return response




AES_KEY = b'78pouythyuiolkjyuioplmngtyuioiuy'  # Exactly 32 bytes for AES-256
AES_IV = b'htyuiokjhytuiopr'  # Exactly 16 bytes

def encrypt_aes(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_aes(encrypted_data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decoded_encrypted_data = base64.b64decode(encrypted_data)
    decrypted_data = cipher.decrypt(decoded_encrypted_data)
    return unpad(decrypted_data, AES.block_size).decode('utf-8')

class AesEncryptionMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'POST' and request.body:
            try:
                # Decrypt the incoming data
                decrypted_data = decrypt_aes(request.body.decode('utf-8'))
                print('decrypted_data: ', decrypted_data)
                request._body = decrypted_data.encode('utf-8')
            except Exception as e:
                raise ValueError("Decryption failed: " + str(e))

    def process_response(self, request, response):
        if response['Content-Type'] == 'application/json':
            try:
                # Encrypt the outgoing response
                encrypted_data = encrypt_aes(response.content.decode('utf-8'))
                response.content =  encrypted_data.encode('utf-8')
            except Exception as e:
                raise ValueError("Encryption failed: " + str(e))
        return response

