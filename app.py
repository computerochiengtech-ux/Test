from flask import Flask, request, jsonify
import requests
import base64
import datetime
import json
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Configuration
business_short_code = "174379"
lipa_na_mpesa_online_passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
consumer_key = "YRIrI8zbw1H5qBQSbZlxOlwhJEWAFcBKKHcco7woaPcU2oso"
consumer_secret = "7HBvVoB7Kop9wQjCeemKDvH03ihASsI5BC2jokRq6jRKVhWleV0B2DKPGbJaIpNj"
callback_url = "https://your-deployment-url.com/callback"  # Replace after deploying

@app.route('/stk_push', methods=['POST'])
def stk_push():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount")

    if not phone or not amount:
        return jsonify({"error": "Phone and amount are required"}), 400

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((business_short_code + lipa_na_mpesa_online_passkey + timestamp).encode()).decode('utf-8')

    # Get access token
    r = requests.get("https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
                     auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = r.json().get("access_token")

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": business_short_code,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": "Payment",
        "TransactionDesc": "Payment of Goods"
    }

    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                              json=payload, headers=headers)

    return jsonify(response.json())

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    with open("callback_log.json", "a") as f:
        json.dump(data, f)
        f.write("\n")
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
