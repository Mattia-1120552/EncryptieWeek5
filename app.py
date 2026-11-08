# Libraries voor het omzetten van tekst, foutmeldingen en willekeurige bytes.
import base64
import binascii
import os

# Cryptography doet de encryptie en Flask regelt de webpagina.
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import Flask, render_template, request

# Maak de app en stel de maximale aanvraaggrootte in op 1 MB.
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024


# Maak een willekeurige sleutel van 128 bits.
def generate_key():
    key = AESGCM.generate_key(bit_length=128)
    # Base64 maakt de sleutel kopieerbaar als tekst.
    return base64.b64encode(key).decode('ascii')


# Zet de ingevoerde sleutel terug naar bytes en controleer de lengte.
def read_key(key_text):
    key = base64.b64decode(key_text.strip(), validate=True)
    if len(key) != 16:
        raise ValueError('De sleutel moet 16 bytes lang zijn.')
    return key


# Versleutel de tekst met de opgegeven sleutel.
def encrypt_text(text, key):
    # GCM heeft bij elke versleuteling met dezelfde sleutel een nieuwe nonce nodig.
    nonce = os.urandom(12)
    # Zet de tekst om naar bytes en laat de library deze versleutelen.
    encrypted = AESGCM(key).encrypt(nonce, text.encode('utf-8'), None)
    # De nonce is openbaar en gaat mee met de tekst en de authenticatietag.
    return base64.b64encode(nonce + encrypted).decode('ascii')


# Zet het versleutelde bericht terug naar de originele tekst.
def decrypt_text(text, key):
    data = base64.b64decode(text.strip(), validate=True)
    # Het bericht bevat minimaal 12 bytes nonce en 16 bytes controletag.
    if len(data) < 28:
        raise ValueError('Het bericht is te kort.')
    # Haal de nonce en de versleutelde inhoud uit elkaar.
    nonce = data[:12]
    encrypted = data[12:]
    # De library controleert het bericht en ontsleutelt het met de sleutel.
    return AESGCM(key).decrypt(nonce, encrypted, None).decode('utf-8')


# Open de pagina met GET of verwerk het formulier met POST.
@app.route('/', methods=['GET', 'POST'])
def index():
    # Begin met lege velden als de pagina wordt geopend.
    text = ''
    key_text = ''
    result = ''
    error = ''

    # Lees de tekst, sleutel en aangeklikte knop uit het formulier.
    if request.method == 'POST':
        text = request.form.get('text', '')
        key_text = request.form.get('key', '')
        action = request.form.get('action', '')

        # Maak een sleutel of controleer of de invoer compleet is.
        if action == 'generate':
            key_text = generate_key()
        elif action not in ('encrypt', 'decrypt'):
            error = 'Kies versleutelen of ontsleutelen.'
        elif not text.strip() or not key_text.strip():
            error = 'Vul tekst en een sleutel in.'
        else:
            # Voer de gekozen actie uit met de ingevoerde sleutel.
            try:
                key = read_key(key_text)
                if action == 'encrypt':
                    result = encrypt_text(text, key)
                else:
                    result = decrypt_text(text, key)
            # Toon een melding als de sleutel niet klopt of het bericht is aangepast.
            except InvalidTag:
                error = 'Ontsleutelen mislukt. De sleutel klopt niet of het bericht is gewijzigd.'
            # Vang ook een ongeldig formaat of een verkeerde sleutellengte op.
            except (ValueError, binascii.Error):
                error = 'Controleer de sleutel en het bericht. Gebruik de volledige gekopieerde waarden.'

    # Geef de ingevulde velden, het resultaat en de foutmelding aan de HTML.
    response = app.make_response(render_template(
        'index.html', text=text, key=key_text, result=result, error=error
    ))
    # Vraag de browser om deze pagina met de sleutel niet te cachen.
    response.headers['Cache-Control'] = 'no-store'
    return response


# Toon een korte melding als de aanvraag groter is dan 1 MB. brrr
@app.errorhandler(413)
def too_large(error):
    return 'De invoer is te groot. Gebruik een korter bericht.', 413


# Start de app op deze computer als je dit bestand uitvoert.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
