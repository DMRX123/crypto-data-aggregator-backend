from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'active',
        'service': 'Crypto Data API',
        'version': '1.0'
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    from data_fetcher import DataFetcher
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data()
    return jsonify(data)

def handler(request):
    return app(request)
