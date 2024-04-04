# Import statements
from flask import Flask, request, make_response, jsonify
import json
import requests
import numpy as np

# Constants
BINANCE_API_BASE_URL = "https://fapi.binance.com/fapi/v1/klines"

# Initialize Flask application
app = Flask(__name__)

# Function to fetch historical data from Binance API
def get_kline_data(symbol, interval='1m'):
    url = f"{BINANCE_API_BASE_URL}?symbol={symbol}&interval={interval}"
    response = requests.get(url)
    # response.raise_for_status()  # Raise exception for HTTP errors
    return response.json()

# Function to calculate EMA
def calculate_ema(data, window=13):
    close_prices = np.array([float(entry[4]) for entry in data])  # Extract closing prices
    ema_values = np.zeros(len(close_prices))  # Initialize array
    alpha = 2 / (window + 1)  # Smoothing factor (alpha)
    ema_values[:window] = np.mean(close_prices[:window])  # Initialize with SMA
    for i in range(window, len(close_prices)):
        ema_values[i] = alpha * close_prices[i] + (1 - alpha) * ema_values[i - 1]
    return ema_values

# Function to process request
def process_request(symbol, interval, indicator, direction='direction_test', callback='callback_test'):
    historical_data = get_kline_data(symbol=symbol, interval=interval)
    ema13_values = calculate_ema(data=historical_data, window=13)
    return ema13_values[-1]

# Flask route to handle HTTP requests
@app.route('/set-alert', methods=['POST'])
def alert_response():
    request_json = request.get_json(silent=True)

    if request_json:
        symbol = request_json.get('symbol')
        interval = request_json.get('interval')
        indicator = request_json.get('indicator')
        # direction = request_json.get('direction')
        # callback = request_json.get('callback')

        if symbol and interval and indicator:
            try:
                response_data = process_request(symbol, interval, indicator) #, direction, callback)
                return make_response(jsonify(response_data), 200)
            except Exception as e:
                return make_response(str(e), 500)
        else:
            return make_response("Missing required parameters: symbol, interval, indicator", 400)
    else:
        return make_response("Request body is empty or not in JSON format", 400)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
