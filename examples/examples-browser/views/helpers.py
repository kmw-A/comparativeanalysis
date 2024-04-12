# from phue import Bridge

# bridge_ip = '192.168.1.5'  
# config_path = '/Users/kevinfred/.python_hue/config.json'  
# b = Bridge(bridge_ip, config_file_path=config_path)

# try:
#     b.connect()  
#     print("Connected to the Philips Hue Bridge.")
# except Exception as e:
#     print(f"Failed to connect to the bridge: {e}")
#     exit(1)

# def list_lights_status():
#     lights = b.get_light_objects('id')
#     for light_id, light in lights.items():
#         print(f"ID: {light_id}, Name: {light.name}, Reachable: {light.reachable}")

# list_lights_status()


from phue import Bridge
import json

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

# Fetch and print the entire information for all lights
def print_all_lights_info():
    all_lights_info = b.get_api()['lights']
    print(json.dumps(all_lights_info, indent=4))  # Pretty print the information

print_all_lights_info()




from flask import Flask, request, jsonify
from flask_cors import CORS
from phue import Bridge
import threading
from collections import deque
import time

app = Flask(__name__)
CORS(app)

bridge_ip = '192.168.1.5'
config_path = '/Users/kevinfred/.python_hue/config.json'
#b = Bridge(bridge_ip, config_file_path=config_path)
b = Bridge(bridge_ip, config_file_path=config_path)
b.connect()

emotion_history = deque(maxlen=5)
update_lock = threading.Lock()

def determine_predominant_emotion(emotion_scores):
    """Determines the emotion with the highest score."""
    print('Determining predominant emotion with scores:', emotion_scores)
    return max(emotion_scores, key=emotion_scores.get)

def categorize_emotion(emotion):
    """Categorizes the given emotion into positive, neutral, or negative."""
    print('Categorizing emotion:', emotion)
    if emotion in ['happiness', 'surprise', 'joy']:
        return 'positive'
    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
        return 'negative'
    else:
        return 'neutral'

# def set_light_based_on_emotion(emotion_category):
#     """Sets the light color based on the categorized emotion."""
#     print('Setting light based on emotion category:', emotion_category)
#     light_settings = {
#         'positive': {'hue': 12750, 'sat': 254, 'bri': 254},
#         'neutral': {'hue': 46920, 'sat': 120, 'bri': 180},
#         'negative': {'hue': 46920, 'sat': 254, 'bri': 254}
#     }
#     settings = light_settings.get(emotion_category, light_settings['neutral'])
#     for light in b.lights:
#         b.set_light(light.light_id, {'on': True, 'hue': settings['hue'], 'sat': settings['sat'], 'bri': settings['bri']})
#     time.sleep(5)
#     for light in b.lights:
#         b.set_light(light.light_id, {'on': False})


# def set_light_based_on_emotion(emotion_category):
#     """Sets the light color based on the categorized emotion."""
#     print('Setting light based on emotion category:', emotion_category)
#     light_settings = {
#         'positive': {'hue': 12750, 'sat': 254, 'bri': 254},
#         'neutral': {'hue': 46920, 'sat': 120, 'bri': 180},
#         'negative': {'hue': 46920, 'sat': 254, 'bri': 254}
#     }
#     settings = light_settings.get(emotion_category, light_settings['neutral'])
#     for light in b.lights:
#         b.set_light(light.light_id, {'on': True, 'hue': settings['hue'], 'sat': settings['sat'], 'bri': settings['bri']})
#     time.sleep(5)  # Delay before turning off the lights
#     for light in b.lights:
#         b.set_light(light.light_id, {'on': False})
#     time.sleep(3)  # Add a small delay before allowing the next emotion update
def set_light_based_on_emotion(emotion_category):
    """Sets the light color based on the categorized emotion."""
    print('Setting light based on emotion category:', emotion_category)
    # light_settings = {
    #     'positive': {'hue': 12750, 'sat': 254, 'bri': 254},
    #     'neutral': {'hue': 46920, 'sat': 120, 'bri': 180},
    #     'negative': {'hue': 46920, 'sat': 254, 'bri': 254}
    # }
    light_settings = {
        'positive': {'hue': 25500, 'sat': 254, 'bri': 254},  # Green
        'neutral': {'hue': 46920, 'sat': 254, 'bri': 254},  # Blue
        'negative': {'hue': 65535, 'sat': 254, 'bri': 254}  # Red
    }
    settings = light_settings.get(emotion_category, light_settings['neutral'])
    for light in b.lights:
        b.set_light(light.light_id, {'on': True, 'hue': settings['hue'], 'sat': settings['sat'], 'bri': settings['bri'], 'transitiontime': 10})

@app.route('/receive_emotion', methods=['POST'])
def receive_emotion():
    """Receives emotional data and updates the lights accordingly."""
    data = request.json
    print("Received data:", data)  # Print the received data

    emotion_scores = {
        'happiness': max(data.get('Face API_happy', 0), data.get('Affectiva_joy', 0)),
        'sadness': data.get('Face API_sad', 0) + data.get('Affectiva_sadness', 0),
        'anger': data.get('Face API_angry', 0) + data.get('Affectiva_anger', 0),
        'fear': data.get('Face API_fearful', 0) + data.get('Affectiva_fear', 0),
        'disgust': data.get('Face API_disgusted', 0) + data.get('Affectiva_disgust', 0),
        'surprise': data.get('Face API_surprised', 0) + data.get('Affectiva_surprise', 0),
        'neutral': data.get('Face API_neutral', 0)
    }
    print("Emotion scores:", emotion_scores)  # Print the emotion scores

    predominant_emotion = determine_predominant_emotion(emotion_scores)
    print("Predominant emotion:", predominant_emotion)  # Print the predominant emotion

    emotion_category = categorize_emotion(predominant_emotion)
    print("Emotion category:", emotion_category)  # Print the emotion category

    with update_lock:
        emotion_history.append(emotion_category)
        if emotion_history.count(emotion_history[-1]) == len(emotion_history):
            threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()
            emotion_history.clear()
    
    return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
















from flask import Flask, request, jsonify
from flask_cors import CORS
from phue import Bridge
import threading
from collections import deque
import time

app = Flask(__name__)
CORS(app)

bridge_ip = '192.168.1.5'
config_path = '/Users/kevinfred/.python_hue/config.json'
b = Bridge(bridge_ip, config_file_path=config_path)
b.connect()

emotion_history = deque(maxlen=5)
update_lock = threading.Lock()

def determine_predominant_emotion(emotion_scores):
    """Determines the emotion with the highest score."""
    print('Determining predominant emotion with scores:', emotion_scores)
    return max(emotion_scores, key=emotion_scores.get)

def categorize_emotion(emotion):
    """Categorizes the given emotion into positive, neutral, or negative."""
    print('Categorizing emotion:', emotion)
    if emotion in ['happiness', 'surprise', 'joy']:
        return 'positive'
    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
        return 'negative'
    else:
        return 'neutral'

def set_light_based_on_emotion(emotion_category):
    """Sets the light color based on the categorized emotion."""
    print('Setting light based on emotion category:', emotion_category)
    light_settings = {
        'positive': {'name': 'Hue lightstrip plus 1'},  # Yellow
        'neutral': {'name': 'energize'},  # White
        'negative': {'name': 'cold'}   # Cold
    }
    settings = light_settings.get(emotion_category, light_settings['neutral'])
    light_name = settings['name']
    light = b.get_light_by_name(light_name)
    if light:
        light.on = True
        light.transitiontime = 50  # 5-second transition time
    else:
        print(f"Light '{light_name}' not found.")

@app.route('/receive_emotion', methods=['POST'])
def receive_emotion():
    """Receives emotional data and updates the lights accordingly."""
    data = request.json
    print("Received data:", data)  # Print the received data

    emotion_scores = {
        'happiness': max(data.get('Face API_happy', 0), data.get('Affectiva_joy', 0)),
        'sadness': data.get('Face API_sad', 0) + data.get('Affectiva_sadness', 0),
        'anger': data.get('Face API_angry', 0) + data.get('Affectiva_anger', 0),
        'fear': data.get('Face API_fearful', 0) + data.get('Affectiva_fear', 0),
        'disgust': data.get('Face API_disgusted', 0) + data.get('Affectiva_disgust', 0),
        'surprise': data.get('Face API_surprised', 0) + data.get('Affectiva_surprise', 0),
        'neutral': data.get('Face API_neutral', 0)
    }
    print("Emotion scores:", emotion_scores)  # Print the emotion scores

    predominant_emotion = determine_predominant_emotion(emotion_scores)
    print("Predominant emotion:", predominant_emotion)  # Print the predominant emotion

    emotion_category = categorize_emotion(predominant_emotion)
    print("Emotion category:", emotion_category)  # Print the emotion category

    with update_lock:
        emotion_history.append(emotion_category)
        if emotion_history.count(emotion_history[-1]) >= len(emotion_history) // 2:
            threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()
            emotion_history.clear()
    
    return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')








from flask import Flask, request, jsonify
from flask_cors import CORS
from phue import Bridge
import threading
from collections import deque
import time

app = Flask(__name__)
CORS(app)

bridge_ip = '192.168.1.5'
config_path = '/Users/kevinfred/.python_hue/config.json'
b = Bridge(bridge_ip, config_file_path=config_path)
b.connect()

emotion_history = deque(maxlen=5)
update_lock = threading.Lock()

def determine_predominant_emotion(emotion_scores):
    """Determines the emotion with the highest score."""
    print('Determining predominant emotion with scores:', emotion_scores)
    return max(emotion_scores, key=emotion_scores.get)

def categorize_emotion(emotion):
    """Categorizes the given emotion into positive, neutral, or negative."""
    print('Categorizing emotion:', emotion)
    if emotion in ['happiness', 'surprise', 'joy']:
        return 'positive'
    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
        return 'negative'
    else:
        return 'neutral'

def set_light_based_on_emotion(emotion_category):
    """Sets the light color based on the categorized emotion."""
    print('Setting light based on emotion category:', emotion_category)
    light_settings = {
        'positive': {'hue': 25500, 'sat': 254, 'bri': 254},  # Green
        'neutral': {'hue': 46920, 'sat': 254, 'bri': 254},  # Blue
        'negative': {'hue': 65535, 'sat': 254, 'bri': 254}   # Red
    }
    settings = light_settings.get(emotion_category, light_settings['neutral'])
    lights = b.get_light_objects('id')
    for light_id in lights:
        b.set_light(light_id, 'on', True)
        b.set_light(light_id, {'hue': settings['hue'], 'sat': settings['sat'], 'bri': settings['bri'], 'transitiontime': 50})


@app.route('/receive_emotion', methods=['POST'])
def receive_emotion():
    """Receives emotional data and updates the lights accordingly."""
    data = request.json
    print("Received data:", data)  # Print the received data

    emotion_scores = {
        'happiness': max(data.get('Face API_happy', 0), data.get('Affectiva_joy', 0)),
        'sadness': data.get('Face API_sad', 0) + data.get('Affectiva_sadness', 0),
        'anger': data.get('Face API_angry', 0) + data.get('Affectiva_anger', 0),
        'fear': data.get('Face API_fearful', 0) + data.get('Affectiva_fear', 0),
        'disgust': data.get('Face API_disgusted', 0) + data.get('Affectiva_disgust', 0),
        'surprise': data.get('Face API_surprised', 0) + data.get('Affectiva_surprise', 0),
        'neutral': data.get('Face API_neutral', 0)
    }
    print("Emotion scores:", emotion_scores)  # Print the emotion scores

    predominant_emotion = determine_predominant_emotion(emotion_scores)
    print("Predominant emotion:", predominant_emotion)  # Print the predominant emotion

    emotion_category = categorize_emotion(predominant_emotion)
    print("Emotion category:", emotion_category)  # Print the emotion category

    with update_lock:
        emotion_history.append(emotion_category)
        if emotion_history.count(emotion_history[-1]) >= len(emotion_history) // 2:
            threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()
            emotion_history.clear()
    
    return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')