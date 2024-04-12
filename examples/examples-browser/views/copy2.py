# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from phue import Bridge
# import threading
# from collections import deque
# import time
# import csv
# import os
# import logging
# from logging.handlers import RotatingFileHandler

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)

# # Setup logging to file
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=5)
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# app.logger.addHandler(file_handler)

# # Philips Hue Bridge setup
# bridge_ip = '192.168.1.5'
# config_path = '/Users/kevinfred/.python_hue/config.json'
# bridge = Bridge(bridge_ip, config_file_path=config_path)

# try:
#     bridge.connect()
#     app.logger.info("Connected to the Philips Hue Bridge.")
# except Exception as e:
#     app.logger.error("Failed to connect to the bridge: %s", e)
#     exit(1)

# emotion_history = deque(maxlen=5)
# update_lock = threading.Lock()
# csv_file_lock = threading.Lock()
# csv_file_path = 'emotion_data.csv'
# server_csv_file_path = 'server_emotion_data.csv'

# # Ensure CSV files exist and have correct headers
# def ensure_csv_files():
#     if not os.path.exists(csv_file_path):
#         with open(csv_file_path, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'predominant_emotion', 'emotion_category'])

#     if not os.path.exists(server_csv_file_path):
#         with open(server_csv_file_path, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'predominant_emotion', 'emotion_category'])

# ensure_csv_files()

# def append_to_csv(data, predominant_emotion, emotion_category):
#     with csv_file_lock:
#         with open(csv_file_path, mode='a', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])
#         with open(server_csv_file_path, mode='a', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])

# def determine_predominant_emotion(emotion_scores):
#     return max(emotion_scores, key=emotion_scores.get)

# def categorize_emotion(emotion):
#     if emotion in ['happiness', 'surprise', 'joy']:
#         return 'positive'
#     elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
#         return 'negative'
#     else:
#         return 'neutral'

# # def set_light_based_on_emotion(emotion_category):
# #     light_settings = {
# #         'positive': {'hue': 25500, 'sat': 254, 'bri': 254},  # Green
# #         'neutral': {'hue': 46920, 'sat': 254, 'bri': 254},   # Blue
# #         'negative': {'hue': 65535, 'sat': 254, 'bri': 254}   # Red
# #     }
# #     settings = light_settings.get(emotion_category, {})
# #     lights = bridge.get_light_objects('id')
# #     for light_id in lights:
# #         bridge.set_light(light_id, {'on': True, **settings, 'transitiontime': 50})
# #         time.sleep(5)  # Maintain color for 5 seconds before turning off
# #         bridge.set_light(light_id, 'on', False)

# from datetime import datetime, timedelta

# # Global variable to store the time of the last request
# from datetime import datetime, timedelta

# # Global variable to store the time of the last request
# last_request_time = datetime.min

# def set_light_based_on_emotion(emotion_category):
#     global last_request_time
#     now = datetime.now()

#     # Check if enough time has passed since the last request
#     if now - last_request_time < timedelta(seconds=5):
#         # Not enough time has passed, skip this request
#         app.logger.info("Skipping light update due to debounce timing.")
#         return

#     # Update the last request time
#     last_request_time = now

#     light_settings = {
#         'positive': {'hue': 25500, 'sat': 254, 'bri': 254},  # Green
#         'neutral': {'hue': 46920, 'sat': 254, 'bri': 254},   # Blue
#         'negative': {'hue': 65535, 'sat': 254, 'bri': 254}   # Red
#     }
#     settings = light_settings.get(emotion_category, {})
#     lights = bridge.get_light_objects('id')
#     for light_id in lights:
#         try:
#             bridge.set_light(light_id, {'on': True, **settings, 'transitiontime': 50})
#             time.sleep(5)  # Maintain color for 5 seconds before turning off
#             bridge.set_light(light_id, 'on', False)
#         except Exception as e:
#             app.logger.error(f"Error setting light: {e}")

#     app.logger.info("Light updated based on emotion.")


# @app.route('/receive_emotion', methods=['POST'])
# def receive_emotion():
#     data = request.json
#     face_api_data = data.get('face_api_data', {})
#     affectiva_data = data.get('affectiva_data', {})

#     emotion_scores = {
#         'happiness': max(face_api_data.get('Face API_happy', 0), affectiva_data.get('Affectiva_joy', 0)),
#         'sadness': max(face_api_data.get('Face API_sad', 0), affectiva_data.get('Affectiva_sadness', 0)),
#         'anger': max(face_api_data.get('Face API_angry', 0), affectiva_data.get('Affectiva_anger', 0)),
#         'fear': max(face_api_data.get('Face API_fearful', 0), affectiva_data.get('Affectiva_fear', 0)),
#         'disgust': max(face_api_data.get('Face API_disgusted', 0), affectiva_data.get('Affectiva_disgust', 0)),
#         'surprise': max(face_api_data.get('Face API_surprised', 0), affectiva_data.get('Affectiva_surprise', 0)),
#         'neutral': max(face_api_data.get('Face API_neutral', 0), 0)  # Assuming 'neutral' is calculated or passed in somehow
#     }

#     predominant_emotion = determine_predominant_emotion(emotion_scores)
#     emotion_category = categorize_emotion(predominant_emotion)
#     logging.info("Emotion data: %s", emotion_scores)

#     append_to_csv(emotion_scores, predominant_emotion, emotion_category)

#     with update_lock:
#         emotion_history.append(emotion_category)
#         if emotion_history.count(emotion_history[-1]) == len(emotion_history):
#             threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()
#             emotion_history.clear()

#     app.logger.info("Processed emotion data and updated lights accordingly.")
#     return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')




from flask import Flask, request, jsonify
from flask_cors import CORS
from phue import Bridge
import threading
from collections import deque
import time
import csv
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging to file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(file_handler)

# Philips Hue Bridge setup
bridge_ip = '192.168.1.5'
config_path = '/Users/kevinfred/.python_hue/config.json'
bridge = Bridge(bridge_ip, config_file_path=config_path)

try:
    bridge.connect()
    app.logger.info("Connected to the Philips Hue Bridge.")
except Exception as e:
    app.logger.error("Failed to connect to the bridge: %s", e)
    exit(1)

emotion_history = deque(maxlen=5)
update_lock = threading.Lock()
csv_file_lock = threading.Lock()
csv_file_path = 'emotion_data.csv'
server_csv_file_path = 'server_emotion_data.csv'

# Ensure CSV files exist and have correct headers
def ensure_csv_files():
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'predominant_emotion', 'emotion_category'])

    if not os.path.exists(server_csv_file_path):
        with open(server_csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'predominant_emotion', 'emotion_category'])

ensure_csv_files()

def append_to_csv(data, predominant_emotion, emotion_category):
    with csv_file_lock:
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])
        with open(server_csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])

def determine_predominant_emotion(emotion_scores):
    return max(emotion_scores, key=emotion_scores.get)

def categorize_emotion(emotion):
    if emotion in ['happiness', 'surprise', 'joy']:
        return 'positive'
    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
        return 'negative'
    else:
        return 'neutral'

# def set_light_based_on_emotion(emotion_category):
#     light_settings = {
#         'positive': {'hue': 25500, 'sat': 254, 'bri': 254},  # Green
#         'neutral': {'hue': 46920, 'sat': 254, 'bri': 254},   # Blue
#         'negative': {'hue': 65535, 'sat': 254, 'bri': 254}   # Red
#     }
#     settings = light_settings.get(emotion_category, {})
#     lights = bridge.get_light_objects('id')
#     for light_id in lights:
#         bridge.set_light(light_id, {'on': True, **settings, 'transitiontime': 50})
#         time.sleep(5)  # Maintain color for 5 seconds before turning off
#         bridge.set_light(light_id, 'on', False)

from datetime import datetime, timedelta

# Global variable to store the time of the last request
from datetime import datetime, timedelta

# Global variable to store the time of the last request
last_request_time = datetime.min

def set_light_based_on_emotion(emotion_category):
    global last_request_time
    now = datetime.now()

    # Check if enough time has passed since the last request
    if now - last_request_time < timedelta(seconds=5):
        # Not enough time has passed, skip this request
        app.logger.info("Skipping light update due to debounce timing.")
        return

    # Update the last request time
    last_request_time = now

    light_settings = {
        'positive': {'hue': 25500, 'sat': 254, 'bri': 254},  # Green
        'neutral': {'hue': 46920, 'sat': 254, 'bri': 254},   # Blue
        'negative': {'hue': 65535, 'sat': 254, 'bri': 254}   # Red
    }
    settings = light_settings.get(emotion_category, {})
    lights = bridge.get_light_objects('id')
    for light_id in lights:
        try:
            bridge.set_light(light_id, {'on': True, **settings, 'transitiontime': 50})
            time.sleep(5)  # Maintain color for 5 seconds before turning off
            bridge.set_light(light_id, 'on', False)
        except Exception as e:
            app.logger.error(f"Error setting light: {e}")

    app.logger.info("Light updated based on emotion.")


@app.route('/receive_emotion', methods=['POST'])
def receive_emotion():
    data = request.json
    face_api_data = data.get('face_api_data', {})
    affectiva_data = data.get('affectiva_data', {})

    emotion_scores = {
        'happiness': max(face_api_data.get('Face API_happy', 0), affectiva_data.get('Affectiva_joy', 0)),
        'sadness': max(face_api_data.get('Face API_sad', 0), affectiva_data.get('Affectiva_sadness', 0)),
        'anger': max(face_api_data.get('Face API_angry', 0), affectiva_data.get('Affectiva_anger', 0)),
        'fear': max(face_api_data.get('Face API_fearful', 0), affectiva_data.get('Affectiva_fear', 0)),
        'disgust': max(face_api_data.get('Face API_disgusted', 0), affectiva_data.get('Affectiva_disgust', 0)),
        'surprise': max(face_api_data.get('Face API_surprised', 0), affectiva_data.get('Affectiva_surprise', 0)),
        'neutral': max(face_api_data.get('Face API_neutral', 0), 0)  # Assuming 'neutral' is calculated or passed in somehow
    }

    predominant_emotion = determine_predominant_emotion(emotion_scores)
    emotion_category = categorize_emotion(predominant_emotion)
    logging.info("Emotion data: %s", emotion_scores)

    append_to_csv(emotion_scores, predominant_emotion, emotion_category)

    with update_lock:
        emotion_history.append(emotion_category)
        if emotion_history.count(emotion_history[-1]) == len(emotion_history):
            threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()
            emotion_history.clear()

    app.logger.info("Processed emotion data and updated lights accordingly.")
    return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
