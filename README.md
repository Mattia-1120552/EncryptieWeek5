# Tekst versleutelen

Voor Security & Cyberwarfare heb ik een kleine Python-webapp gemaakt waarmee je tekst kunt versleutelen en ontsleutelen. De interface bestaat uit HTML en basis-CSS. Flask verwerkt het formulier en de library `cryptography` voert de encryptie uit.

[GitHub-repository](https://github.com/Mattia-1120552/EncryptieWeek5)

## Starten

Installeer Python 3.11 of hoger. Open een terminal in deze map en voer uit.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

all gebruik je de fish terminal is de tweede command iets anders

```bash
source .venv/bin/activate.fish
```

Open daarna http://127.0.0.1:5000 in je browser.

## Gebruiken

1. Vul tekst in.
2. Klik op **Genereer sleutel** en bewaar de getoonde sleutel veilig.
3. Klik op **Versleutel** en kopieer het resultaat.
4. Plak het resultaat in het bovenste tekstvak.
5. Gebruik dezelfde sleutel en klik op **Ontsleutel**.

Bij lege invoer, een ongeldige sleutel of een beschadigd bericht verschijnt een foutmelding. De oorspronkelijke tekst behoudt spaties, nieuwe regels en bijzondere tekens. Een nieuwe sleutel vervangt de waarde in het sleutelveld. Bewaar dus eerst de oude sleutel als je daarmee berichten hebt versleuteld.

## Encryptiemethoden

Bij symmetrische encryptie gebruik je dezelfde geheime sleutel voor versleutelen en ontsleutelen. Dit werkt snel, maar beide personen moeten de sleutel veilig ontvangen en bewaren.

Asymmetrische encryptie gebruikt een publieke en een privésleutel. Bij bijvoorbeeld RSA-encryptie kan iemand met je publieke sleutel een bericht voor je versleutelen. Je privésleutel is nodig om het te ontsleutelen. In de praktijk worden beide methoden vaak gecombineerd. Asymmetrische technieken helpen bij het opzetten van een gedeeld geheim, waarna symmetrische encryptie de gegevens beschermt.

Deze app gebruikt **AES-128-GCM**. AES is een gestandaardiseerd symmetrisch algoritme. Een willekeurige sleutel van 128 bits is geschikt voor deze opdracht. GCM voegt een controle toe waarmee wijzigingen aan het bericht worden ontdekt. De library weigert het bericht als deze controle mislukt, bijvoorbeeld door een verkeerde sleutel.

Ik gebruik de bestaande `AESGCM`-klasse van `cryptography`. De cryptografische berekeningen worden door de library uitgevoerd. Dit past bij het principe “Don't roll your own crypto”.

## Sleutelbeheer

De knop **Genereer sleutel** gebruikt `AESGCM.generate_key` om een cryptografisch willekeurige sleutel van 16 bytes te maken. Base64 maakt deze bytes kopieerbaar als tekst. Base64 is alleen een manier om bytes weer te geven en biedt zelf geen beveiliging.

De sleutel staat tijdens gebruik in het formulier en wordt bij een actie naar de lokale Flask-app gestuurd. De app schrijft de sleutel en berichten niet naar een bestand of database. Ze zijn wel tijdelijk aanwezig in het geheugen en zichtbaar in de browser. Iemand met toegang tot de computer kan ze mogelijk lezen. De gebruiker moet de sleutel zelf bewaren, bijvoorbeeld in een wachtwoordmanager. Zonder sleutel is er geen herstelmogelijkheid. Wie de sleutel bezit, kan de bijbehorende berichten ontsleutelen en geldige nieuwe berichten maken.

Bij elke versleuteling wordt een willekeurige nonce van 12 bytes gemaakt. Een nonce mag bij dezelfde sleutel niet worden hergebruikt. De willekeurige generatie maakt een botsing voor het kleine gebruik van deze app zeer onwaarschijnlijk. De nonce, versleutelde tekst en authenticatietag worden samen als Base64 teruggegeven. De nonce hoeft niet geheim te blijven. De sleutel zit niet in dit resultaat.

De app regelt geen automatische sleuteluitwisseling. Om een bericht te delen moet je de sleutel apart via een beveiligd kanaal overdragen, bijvoorbeeld persoonlijk. Je moet daarbij ook controleren of je met de juiste persoon deelt. Als de sleutel uitlekt, moeten gebruikers een nieuwe sleutel afspreken. Oude berichten blijven met de oude sleutel leesbaar.

Bij veel gebruikers wordt dit ingewikkelder. Met een aparte sleutel voor ieder paar zijn er bij n gebruikers maximaal n × (n − 1) / 2 sleutels nodig. Met één groepssleutel kan iedereen in de groep alle groepsberichten lezen. Als iemand vertrekt of een sleutel uitlekt, moet de groepssleutel opnieuw worden verdeeld.

Bij online hosting zou de server de tekst en sleutel ook ontvangen. Daar zijn onder andere HTTPS en passend serverbeheer nodig. Deze versie luistert alleen op de eigen computer.

## Kerckhoffs' principe

Volgens Kerckhoffs moet een systeem veilig blijven als de werking bekend is en alleen de sleutel geheim blijft. Dat past bij deze app. De broncode staat op GitHub en het gebruikte algoritme is openbaar. Ook de nonce mag bekend zijn. Zonder de geheime sleutel hoort iemand de versleutelde tekst niet te kunnen lezen.

Het geheimhouden van de code is dus geen onderdeel van de beveiliging. Wel moeten de library correct gebruikt worden en de sleutel geheim blijven. Een veilige encryptiemethode helpt niet als iemand de sleutel samen met het bericht openbaar deelt.

## Bestanden

- `app.py` verwerkt het formulier en bevat de encryptiefuncties.
- `templates/index.html` bevat de webpagina.
- `static/style.css` bevat de opmaak.
- `requirements.txt` bevat de benodigde libraries.

## Bronnen

- [cryptography – AESGCM, sleutelgeneratie en noncegebruik](https://cryptography.io/en/stable/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM)
- [Flask – Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [NIST – Advanced Encryption Standard](https://doi.org/10.6028/NIST.FIPS.197-upd1)
- [Kerckhoffs – La cryptographie militaire (1883)](https://www.petitcolas.net/kerckhoffs/)

## Inleveren

Push de bestanden naar de GitHub-repository en upload deze README met de repositorylink in Brightspace.
