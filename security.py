##pip install face_recognition opencv-python Flask pycryptodome

--
import face_recognition
import cv2
import os
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

app = Flask(__name__)

# Load known face encodings
known_face_encodings = []
known_face_names = []

def load_known_faces():
    for file_name in os.listdir('known_faces'):
        image = face_recognition.load_image_file(f'known_faces/{file_name}')
        face_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(os.path.splitext(file_name)[0])

load_known_faces()

# Encryption setup
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return base64.b64encode(nonce + ciphertext).decode('utf-8')

def decrypt_data(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data)
    nonce = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt(ciphertext)
    return data.decode('utf-8')

key = hashlib.sha256(b'secret_key').digest()

# Flask route for biometric authentication
@app.route('/authenticate', methods=['POST'])
def authenticate():
    file = request.files['file']
    image = face_recognition.load_image_file(file)
    face_encodings = face_recognition.face_encodings(image)
    
    if len(face_encodings) == 0:
        return jsonify({'error': 'No face detected'}), 400

    face_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    
    if True in matches:
        first_match_index = matches.index(True)
        name = known_face_names[first_match_index]
        encrypted_name = encrypt_data(name.encode(), key)
        return jsonify({'status': 'success', 'user': encrypted_name}), 200
    else:
        return jsonify({'status': 'failure', 'error': 'Authentication failed'}), 401

if __name__ == '__main__':
    app.run(debug=True)

#enjoy hyperspace 🖤