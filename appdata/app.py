import os
import requests
import time
import sys
import logging
import pymongo
from flask import Flask, request, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datafunctions import start_scrape_job, check_sold_job
from api import api_summary

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

application = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.add_job(func=start_scrape_job, trigger="interval", seconds=120)
scheduler.add_job(func=check_sold_job, trigger="interval", days=1)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/summary', methods=['GET'])
def summary():
    data = api_summary()
    return jsonify(
        status=True,
        data=data
        ), 201

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
