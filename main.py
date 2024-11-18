import json
import os

import requests
from dotenv import load_dotenv
from epaycosdk.epayco import Epayco
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

epayco = Epayco({
    'apiKey': os.getenv('EPAYCO_PUBLIC_KEY'),
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
    except Exception as e:
        return {'error': str(e)}

def create_customer(token, data):
    customer_info = {'name': data['name'], 'last_name': data['last_name'], 'email': data['email'],
                     'phone': data['phone'], 'default': True, 'token_card': token}
    try:
        customer = epayco.customer.create(customer_info)
        return customer
    except Exception as e:
        return {'error': str(e)}


# Función para enviar el correo de notificación al microservicio de correos
def send_email(subject, recipient_email, body_html):
    try:
        url_notificaciones = "http://localhost:5000/send-email"  # URL del microservicio de correos
        data = {
            "subject": subject,
            "recipient": recipient_email,
            "body_html": body_html
        }
        response = requests.post(url_notificaciones, json=data)

        if response.status_code == 200:
            print("Correo enviado exitosamente.")
        else:
            print(f"Error al enviar el correo: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


# Tu función de procesar el pago
def procces_payment(data, customer_id, token_card):
    try:
        payment_info = {
            'token_card': token_card,
            'customer_id': customer_id,
            'doc_type': 'CC',
            'doc_number': data['doc_number'],
            'name': data['name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'city': data['city'],
            'address': data['address'],
            'phone': data['phone'],
            'cell_phone': data['cell_phone'],
            'bill': data['bill'],
            'description': 'Pago de servicios',
            'value': data['value'],
            'tax': '0',
            'tax_base': data['value'],
            'currency': 'COP'
        }
        response = epayco.charge.create(payment_info)

        if response["status"] is False:
            return response

        # Si el pago es exitoso, enviar un correo
        if response['data']['estado'] == 'Aceptada' and response['data']['respuesta'] == 'Aprobada':
            subject = "Pago Aprobado"
            body_html = f"""
            <h1>¡Pago Aprobado!</h1>
            <p>Estimado(a) {data['name']} {data['last_name']},</p>
            <p>Su pago con factura <strong>{data['bill']}</strong> ha sido aprobado.</p>
            """
            send_email(subject, data['email'], body_html)

        return response
    except Exception as e:
        return {'error': str(e)}


@app.route('/process-payment', methods=['POST'])
def handle_process_payment():
    data = request.json

    token_response = create_token(data)
    print("Token response", json.dumps(token_response))

    if token_response["status"] is False:
        return jsonify(token_response), 500

    token_card = token_response['id']

    customer_response = create_customer(token_card, data)
    print("Customer response", json.dumps(customer_response))

    if 'error' in customer_response:
        return jsonify(customer_response), 500

    customer_id = customer_response['data']['customerId']

    payment_response = procces_payment(data, customer_id, token_card)
    print("Payment response", json.dumps(payment_response))

    if 'error' in payment_response:
        return jsonify(payment_response), 500

    return jsonify(payment_response), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)