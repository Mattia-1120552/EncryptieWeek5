import base64
import binascii
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import Flask, render_template, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024


def generate_key():
    key = AESGCM.generate_key(bit_length=128)
    return base64.b64encode(key).decode('ascii')


def read_key(key_text):
    key = base64.b64decode(key_text.strip(), validate=True)
    if len(key) != 16:
        raise ValueError('De sleutel moet 16 bytes lang zijn.')
    return key


def encrypt_text(text, key):
    # GCM heeft bij elke versleuteling met dezelfde sleutel een nieuwe nonce nodig.
    nonce = os.urandom(12)
    encrypted = AESGCM(key).encrypt(nonce, text.encode('utf-8'), None)
    # De nonce is openbaar en gaat mee met de tekst en de authenticatietag.
    return base64.b64encode(nonce + encrypted).decode('ascii')


def decrypt_text(text, key):
    data = base64.b64decode(text.strip(), validate=True)
    if len(data) < 28:
        raise ValueError('Het bericht is te kort.')
    nonce = data[:12]
    encrypted = data[12:]
    return AESGCM(key).decrypt(nonce, encrypted, None).decode('utf-8')


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ''
    key_text = ''
    result = ''
    error = ''

    if request.method == 'POST':
        text = request.form.get('text', '')
        key_text = request.form.get('key', '')
        action = request.form.get('action', '')

        if action == 'generate':
            key_text = generate_key()
        elif action not in ('encrypt', 'decrypt'):
            error = 'Kies versleutelen of ontsleutelen.'
        elif not text.strip() or not key_text.strip():
            error = 'Vul tekst en een sleutel in.'
        else:
            try:
                key = read_key(key_text)
                if action == 'encrypt':
                    result = encrypt_text(text, key)
                else:
                    result = decrypt_text(text, key)
            except InvalidTag:
                error = 'Ontsleutelen mislukt. De sleutel klopt niet of het bericht is gewijzigd.'
            except (ValueError, binascii.Error):
                error = 'Controleer de sleutel en het bericht. Gebruik de volledige gekopieerde waarden.'

    response = app.make_response(render_template(
        'index.html', text=text, key=key_text, result=result, error=error
    ))
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.errorhandler(413)
def too_large(error):
    return 'De invoer is te groot. Gebruik een korter bericht.', 413


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
