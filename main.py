import json
import os

from dotenv import load_dotenv
from epaycosdk.epayco import Epayco

load_dotenv()

app = Flask(__name__)

epayco = Epayco({
    'apikey': os.getenv('EPAYCO_PUBLIC_KEY'),
    'privateKey': os.getenv('EPAYCO_PRIVATE_KEY')

})