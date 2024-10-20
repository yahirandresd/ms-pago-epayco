from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Obtener las claves de ePayco desde las variables de entorno
EPAYCO_PUBLIC_KEY = os.getenv("EPAYCO_PUBLIC_KEY")
P_CUST_ID_CLIENTE = os.getenv("P_CUST_ID_CLIENTE")
P_KEY = os.getenv("P_KEY")


# Página principal con el formulario de pago
@app.route('/')
def index():
    return render_template('index.html', epayco_public_key=EPAYCO_PUBLIC_KEY)


# Ruta para manejar la respuesta de ePayco
@app.route('/epayco/response', methods=['POST'])
def epayco_response():
    data = request.json
    print(data)

    # Acceder al token y otros detalles
    token = data.get('token')
    transaction_id = data.get('transactionId')
    amount = data.get('amount')
    currency = data.get('currency')
    email = data.get('email')
    state = data.get('state')

    if token:
        print(f'Token recibido: {token}')

    print(f'Transacción ID: {transaction_id}')
    print(f'Monto: {amount} {currency}')
    print(f'Email: {email}')
    print(f'Estado de la transacción: {state}')

    return jsonify({"status": "success", "data": data})


#if __name__ == "__main__":
    #app.run(debug=True, port=5001)
