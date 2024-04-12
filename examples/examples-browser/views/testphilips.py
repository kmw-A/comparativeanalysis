import logging
from flask import Flask, request, jsonify
from phue import Bridge
import threading
from collections import deque
import time
import json

app = Flask(__name__)

# Initialize the bridge connection
bridge_ip = '192.168.1.5'  # Use the IP address of your Philips Hue Bridge
config_path = '/Users/kevinfred/.python_hue/config.json'  # Configuration file path
b = Bridge(bridge_ip, config_file_path=config_path)

try:
    b.connect()  # Attempt to connect to the bridge
    print("Connected to the Philips Hue Bridge.")
except Exception as e:
    print(f"Failed to connect to the bridge: {e}")
    exit(1)

emotion_history = deque(maxlen=5)  # Stores the last 5 received emotion categories
update_lock = threading.Lock()  # Prevents concurrent updates

def determine_predominant_emotion(emotion_scores):
    """Determines the emotion with the highest score."""
    return max(emotion_scores, key=emotion_scores.get)

def categorize_emotion(emotion):
    """Categorizes the given emotion into positive, neutral, or negative."""
    if emotion in ['happiness', 'surprise']:
        return 'positive'
    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
        return 'negative'
    else:
        return 'neutral'

def set_light_based_on_emotion(emotion_category):
    """Sets the light color based on the categorized emotion."""
    logging.info(f"Attempting to set lights for emotion category: {emotion_category}")
    light_settings = {
        'positive': {'hue': 12750, 'sat': 254, 'bri': 254},
        'neutral': {'hue': 46920, 'sat': 120, 'bri': 180},
        'negative': {'hue': 46920, 'sat': 254, 'bri': 254}
    }
    settings = light_settings.get(emotion_category, light_settings['neutral'])  # Default to neutral
    for light in b.lights:
        b.set_light(light.light_id, {'on': True, 'hue': settings['hue'], 'sat': settings['sat'], 'bri': settings['bri']})
    time.sleep(5)  # Display the color for 5 seconds
    for light in b.lights:
        b.set_light(light.light_id, {'on': False})  # Then turn off the lights

@app.route('/receive_emotion', methods=['POST'])
def receive_emotion():
    """Receives emotional data and updates the lights accordingly."""
    data = request.json
    emotion_scores = {
        'happiness': data.get('happiness', 0),
        'sadness': data.get('sadness', 0),
        'anger': data.get('anger', 0),
        'fear': data.get('fear', 0),
        'disgust': data.get('disgust', 0),
        'surprise': data.get('surprise', 0),
        'neutral': data.get('neutral', 0)
    }
    predominant_emotion = determine_predominant_emotion(emotion_scores)
    emotion_category = categorize_emotion(predominant_emotion)
    with update_lock:
        emotion_history.append(emotion_category)
        # If the latest emotion has been consistent throughout the history
        if emotion_history.count(emotion_history[-1]) == len(emotion_history):
            threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()
            emotion_history.clear()  # Reset history after adjusting lights
    return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})

def test_send_neutral_emotion():
    emotion_data = {
        'neutral': 1.0,
        'happiness': 0.0,
        'sadness': 0.0,
        'anger': 0.0,
        'fear': 0.0,
        'disgust': 0.0,
        'surprise': 0.0
    }
    response = app.test_client().post('/receive_emotion', json=emotion_data)
    print(f"Neutral emotion test - Response: {response.json}")

def test_send_positive_emotion():
    emotion_data = {
        'neutral': 0.0,
        'happiness': 1.0,
        'sadness': 0.0,
        'anger': 0.0,
        'fear': 0.0,
        'disgust': 0.0,
        'surprise': 0.0
    }
    response = app.test_client().post('/receive_emotion', json=emotion_data)
    print(f"Positive emotion test - Response: {response.json}")

def test_send_negative_emotion():
    emotion_data = {
        'neutral': 0.0,
        'happiness': 0.0,
        'sadness': 1.0,
        'anger': 0.0,
        'fear': 0.0,
        'disgust': 0.0,
        'surprise': 0.0
    }
    response = app.test_client().post('/receive_emotion', json=emotion_data)
    print(f"Negative emotion test - Response: {response.json}")

# Uncomment the following lines to run the test functions
# test_send_neutral_emotion()
# test_send_positive_emotion()
# test_send_negative_emotion()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')