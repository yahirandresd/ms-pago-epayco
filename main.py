import json
import os

from dotenv import load_dotenv
from epaycosdk.epayco import Epayco

load_dotenv()

app = Flask(__name__)

epayco = Epayco({
    'apikey': os.getenv('EPAYCO_PUBLIC_KEY'),
    'privateKey': os.getenv('EPAYCO_PRIVATE_KEY'),
    'lenguage': 'ES', #Lenguage pa los messages
    'test': os.getenv('EPAYCO_TEST') == 'true' #true para modo de PRUEBA, false para modo PRODUCCION

})


def create_token(data):
    try:
        card_info = {
            "card[number]": data['card_number'],
            "card[exp_year]": data['exp_year'],
            "card[exp_month]": data['exp_month'],
            "card[cvc]": data['cvc'],
            "hasCvv": True
        }
        token = epayco.token.create(card_info)
        return token
