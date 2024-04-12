# import os
# import time
# import random
# import threading
# import csv
# import logging
# from collections import deque
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from phue import Bridge
# import vlc

# # Basic logging setup
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Flask app setup
# app = Flask(__name__)
# CORS(app)

# # Music directory setup
# music_directories = {
#     'positive': 'music/positive',
#     'neutral': 'music/neutral',
#     'negative': 'music/negative'
# }

# # Philips Hue Bridge setup
# bridge_ip = '192.168.1.5'
# config_path = '/Users/kevinfred/.python_hue/config.json'
# bridge = Bridge(bridge_ip, config_file_path=config_path)

# try:
#     bridge.connect()
#     logging.info("Connected to the Philips Hue Bridge.")
# except Exception as e:
#     logging.error(f"Failed to connect to the bridge: {e}")

# # Threading and CSV setup
# emotion_history = deque(maxlen=10)
# update_lock = threading.Lock()
# csv_file_lock = threading.Lock()
# csv_file_path = 'emotion_data.csv'
# server_csv_file_path = 'server_emotion_data.csv'

# # Ensure the CSV files exist and have the correct headers
# for csv_file in [csv_file_path, server_csv_file_path]:
#     if not os.path.exists(csv_file):
#         with open(csv_file, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'contempt', 'predominant_emotion', 'emotion_category'])

# def append_to_csv(data, predominant_emotion, emotion_category):
#     """ Appends emotion data to both CSV files in a thread-safe manner. """
#     with csv_file_lock:
#         for csv_file in [csv_file_path, server_csv_file_path]:
#             with open(csv_file, mode='a', newline='') as file:
#                 writer = csv.writer(file)
#                 writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])

# def determine_predominant_emotion(emotion_scores):
#     """ Determines the emotion with the highest score. """
#     return max(emotion_scores, key=emotion_scores.get)

# def categorize_emotion(emotion):
#     """ Categorizes the given emotion into positive, neutral, or negative. """
#     if emotion in ['happiness', 'surprise', 'joy']:
#         return 'positive'
#     elif emotion in ['sadness', 'anger', 'fear', 'disgust', 'contempt']:
#         return 'negative'
#     return 'neutral'

# current_player = None
# current_emotion_category = None


# def stop_current_player():
#     global current_player
#     if current_player is not None:
#         current_player.stop()
#         current_player.release()
#         current_player = None
#         logging.info("Stopped and released the current VLC player.")


# def play_random_song(category):
#     global current_player

#     directory = music_directories.get(category)
#     if not directory or not os.path.isdir(directory):
#         logging.info(f"No directory found for category: {category}")
#         return

#     songs = [song for song in os.listdir(directory) if song.endswith('.mp3')]
#     if not songs:
#         logging.info(f"No songs found in category: {category}")
#         return

#     song_to_play = random.choice(songs)
#     full_path_to_song = os.path.join(directory, song_to_play)
#     logging.info(f"Playing {song_to_play} from {category} category.")

#     stop_current_player()
#     current_player = vlc.MediaPlayer(full_path_to_song)
#     current_player.play()



# def set_light_based_on_emotion(emotion_category):
#     global current_emotion_category

#     light_settings = {
#         'positive': {'hue': 25500, 'sat': 254, 'bri': 254, 'transitiontime': 100},
#         'neutral': {'hue': 46920, 'sat': 254, 'bri': 254, 'transitiontime': 100},
#         'negative': {'hue': 65535, 'sat': 254, 'bri': 254, 'transitiontime': 100}
#     }
#     settings = light_settings.get(emotion_category, {})
#     lights = bridge.get_light_objects('id')

#     try:
#         if current_emotion_category != emotion_category:
#             stop_current_player()
#             for light_id in lights:
#                 bridge.set_light(light_id, {'on': True, **settings})
#             current_emotion_category = emotion_category
#             #stop playing music after 50 seconds
#             stop_current_player()
#             play_random_song(emotion_category)
#             time.sleep(50)  
#     except Exception as e:
#         logging.error(f"Error while setting light based on emotion: {e}")

# @app.route('/receive_emotion', methods=['POST'])
# def receive_emotion():
#     try:
#         data = request.json
#         face_api_data = data.get('face_api_data', {})
#         affectiva_data = data.get('affectiva_data', {})

#         emotion_scores = {
#             'happiness': face_api_data.get('Face API_happy', 0) + affectiva_data.get('Affectiva_joy', 0),
#             'sadness': face_api_data.get('Face API_sad', 0) + affectiva_data.get('Affectiva_sadness', 0),
#             'anger': face_api_data.get('Face API_angry', 0) + affectiva_data.get('Affectiva_anger', 0),
#             'fear': face_api_data.get('Face API_fearful', 0) + affectiva_data.get('Affectiva_fear', 0),
#             'disgust': face_api_data.get('Face API_disgusted', 0) + affectiva_data.get('Affectiva_disgust', 0),
#             'surprise': face_api_data.get('Face API_surprised', 0) + affectiva_data.get('Affectiva_surprise', 0),
#             'neutral': face_api_data.get('Face API_neutral', 0),
#             'contempt': affectiva_data.get('Affectiva_contempt', 0)
#         }

#         predominant_emotion = determine_predominant_emotion(emotion_scores)
#         emotion_category = categorize_emotion(predominant_emotion)

#         predominant_emotion = determine_predominant_emotion(emotion_scores)
#         emotion_category = categorize_emotion(predominant_emotion)

#         with update_lock:
#             if emotion_history and emotion_category != emotion_history[-1]:
#                 threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()

#         append_to_csv(emotion_scores, predominant_emotion, emotion_category)
#         emotion_history.append(emotion_category)

#         return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})
#     except Exception as e:
#         logging.error(f"Error while receiving emotion: {e}")
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# if __name__ == '__main__':
#     try:
#         app.run(debug=True, host='0.0.0.0')
#     except KeyboardInterrupt:
#         stop_current_player()
#         logging.info("Program terminated by user.")
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#     finally:
#         stop_current_player()
#         logging.info("Program terminated.")



# import os
# import time
# import random
# import threading
# import csv
# import logging
# from collections import deque
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from phue import Bridge
# import vlc

# #Basic logging setup
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# #Flask app setup
# app = Flask(__name__)
# CORS(app)

# #Music directory setup
# music_directories = {
#     'positive': 'music/positive',
#     'neutral': 'music/neutral',
#     'negative': 'music/negative'
# }

# #Philips Hue Bridge setup
# bridge_ip = '192.168.1.5'
# config_path = '/Users/kevinfred/.python_hue/config.json'
# bridge = Bridge(bridge_ip, config_file_path=config_path)

# try:
#     bridge.connect()
#     logging.info("Connected to the Philips Hue Bridge.")
# except Exception as e:
#     logging.error(f"Failed to connect to the bridge: {e}")

# #Threading and CSV setup
# emotion_history = deque(maxlen=10)
# update_lock = threading.Lock()
# csv_file_lock = threading.Lock()
# csv_file_path = 'emotion_data.csv'
# server_csv_file_path = 'server_emotion_data.csv'
# current_players = []
# current_emotion_category = None


# #Ensure the CSV files exist and have the correct headers
# for csv_file in [csv_file_path, server_csv_file_path]:
#     if not os.path.exists(csv_file):
#         with open(csv_file, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'contempt', 'predominant_emotion', 'emotion_category'])

# def append_to_csv(data, predominant_emotion, emotion_category):
#     """ Appends emotion data to both CSV files in a thread-safe manner. """
#     with csv_file_lock:
#         for csv_file in [csv_file_path, server_csv_file_path]:
#             with open(csv_file, mode='a', newline='') as file:
#                 writer = csv.writer(file)
#                 writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])

# def determine_predominant_emotion(emotion_scores):
#     """ Determines the emotion with the highest score. """
#     return max(emotion_scores, key=emotion_scores.get)

# def categorize_emotion(emotion):
#     """ Categorizes the given emotion into positive, neutral, or negative. """
#     if emotion in ['happiness', 'surprise', 'joy']:
#         return 'positive'
#     elif emotion in ['sadness', 'anger', 'fear', 'disgust', 'contempt']:
#         return 'negative'
#     return 'neutral'



# def stop_current_players():
#     global current_players
#     for player in current_players:
#         player.stop()
#         player.release()
#     current_players = []
#     logging.info("Stopped and released all VLC players.")

# def play_random_song(category):
#     global current_players

#     directory = music_directories.get(category)
#     if not directory or not os.path.isdir(directory):
#         logging.info(f"No directory found for category: {category}")
#         return

#     songs = [song for song in os.listdir(directory) if song.endswith('.mp3')]
#     if not songs:
#         logging.info(f"No songs found in category: {category}")
#         return

#     song_to_play = random.choice(songs)
#     full_path_to_song = os.path.join(directory, song_to_play)
#     logging.info(f"Playing {song_to_play} from {category} category.")

#     stop_current_players()
#     player = vlc.MediaPlayer(full_path_to_song)
#     player.play()
#     current_players.append(player)



# def set_light_based_on_emotion(emotion_category):
#     global current_emotion_category

#     light_settings = {
#         'positive': {'hue': 25500, 'sat': 254, 'bri': 254, 'transitiontime': 100},
#         'neutral': {'hue': 46920, 'sat': 254, 'bri': 254, 'transitiontime': 100},
#         'negative': {'hue': 65535, 'sat': 254, 'bri': 254, 'transitiontime': 100}
#     }
#     settings = light_settings.get(emotion_category, {})
#     lights = bridge.get_light_objects('id')

#     try:
#         if current_emotion_category != emotion_category:
#             stop_current_players()
#             for light_id in lights:
#                 bridge.set_light(light_id, {'on': True, **settings})
#             current_emotion_category = emotion_category
#             play_random_song(emotion_category)
#             time.sleep(50)  
#     except Exception as e:
#         logging.error(f"Error while setting light based on emotion: {e}")

# @app.route('/receive_emotion', methods=['POST'])
# def receive_emotion():
#     try:
#         data = request.json
#         face_api_data = data.get('face_api_data', {})
#         affectiva_data = data.get('affectiva_data', {})

#         emotion_scores = {
#             'happiness': face_api_data.get('Face API_happy', 0) + affectiva_data.get('Affectiva_joy', 0),
#             'sadness': face_api_data.get('Face API_sad', 0) + affectiva_data.get('Affectiva_sadness', 0),
#             'anger': face_api_data.get('Face API_angry', 0) + affectiva_data.get('Affectiva_anger', 0),
#             'fear': face_api_data.get('Face API_fearful', 0) + affectiva_data.get('Affectiva_fear', 0),
#             'disgust': face_api_data.get('Face API_disgusted', 0) + affectiva_data.get('Affectiva_disgust', 0),
#             'surprise': face_api_data.get('Face API_surprised', 0) + affectiva_data.get('Affectiva_surprise', 0),
#             'neutral': face_api_data.get('Face API_neutral', 0),
#             'contempt': affectiva_data.get('Affectiva_contempt', 0)
#         }

#         predominant_emotion = determine_predominant_emotion(emotion_scores)
#         emotion_category = categorize_emotion(predominant_emotion)

#         predominant_emotion = determine_predominant_emotion(emotion_scores)
#         emotion_category = categorize_emotion(predominant_emotion)

#         with update_lock:
#             if emotion_history and emotion_category != emotion_history[-1]:
#                 threading.Thread(target=set_light_based_on_emotion, args=(emotion_category,)).start()

#         append_to_csv(emotion_scores, predominant_emotion, emotion_category)
#         emotion_history.append(emotion_category)

#         return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})
#     except Exception as e:
#         logging.error(f"Error while receiving emotion: {e}")
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# if __name__ == '__main__':
#     try:
#         app.run(debug=True, host='0.0.0.0')
#     except KeyboardInterrupt:
#         stop_current_players()
#         logging.info("Program terminated by user.")
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#     finally:
#         stop_current_players()
#         logging.info("Program terminated.")


import os
import time
import random
import threading
import csv
import logging
from collections import deque
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from phue import Bridge
import vlc

#Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Flask app setup
app = Flask(__name__)
CORS(app)

#Music directory setup
music_directories = {
    'positive': 'music/positive',
    'neutral': 'music/neutral',
    'negative': 'music/negative'
}

#Philips Hue Bridge setup
bridge_ip = '192.168.1.5'
config_path = '/Users/kevinfred/.python_hue/config.json'
bridge = Bridge(bridge_ip, config_file_path=config_path)

try:
    bridge.connect()
    logging.info("Connected to the Philips Hue Bridge.")
except Exception as e:
    logging.error(f"Failed to connect to the bridge: {e}")

#Threading and CSV setup
emotion_history = deque(maxlen=10)
update_lock = threading.Lock()
csv_file_lock = threading.Lock()
csv_file_path = 'emotion_data.csv'
server_csv_file_path = 'server_emotion_data.csv'
current_players = []
current_emotion_category = None

# Smoothing setup
emotion_buffer = deque(maxlen=10)  # Buffer to store the most recent emotions
buffer_threshold = 5  # Number of consecutive detections required to trigger a change

#Ensure the CSV files exist and have the correct headers
for csv_file in [csv_file_path, server_csv_file_path]:
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral', 'contempt', 'predominant_emotion', 'emotion_category'])

def append_to_csv(data, predominant_emotion, emotion_category):
    """ Appends emotion data to both CSV files in a thread-safe manner. """
    with csv_file_lock:
        for csv_file in [csv_file_path, server_csv_file_path]:
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), *data.values(), predominant_emotion, emotion_category])

def determine_predominant_emotion(emotion_scores):
    """ Determines the emotion with the highest score. """
    return max(emotion_scores, key=emotion_scores.get)

def categorize_emotion(emotion):
    """ Categorizes the given emotion into positive, neutral, or negative. """
    if emotion in ['happiness', 'surprise', 'joy']:
        return 'positive'
    elif emotion in ['sadness', 'anger', 'fear', 'disgust', 'contempt']:
        return 'negative'
    return 'neutral'

def stop_current_players():
    global current_players
    for player in current_players:
        player.stop()
        player.release()
    current_players = []
    logging.info("Stopped and released all VLC players.")

def play_random_song(category):
    global current_players

    directory = music_directories.get(category)
    if not directory or not os.path.isdir(directory):
        logging.info(f"No directory found for category: {category}")
        return

    songs = [song for song in os.listdir(directory) if song.endswith('.mp3')]
    if not songs:
        logging.info(f"No songs found in category: {category}")
        return

    song_to_play = random.choice(songs)
    full_path_to_song = os.path.join(directory, song_to_play)
    logging.info(f"Playing {song_to_play} from {category} category.")

    stop_current_players()
    player = vlc.MediaPlayer(full_path_to_song)
    player.play()
    current_players.append(player)

def set_light_based_on_emotion(emotion_category):
    global current_emotion_category

    light_settings = {
        'positive': {'hue': 25500, 'sat': 254, 'bri': 254, 'transitiontime': 100},
        'neutral': {'hue': 46920, 'sat': 254, 'bri': 254, 'transitiontime': 100},
        'negative': {'hue': 65535, 'sat': 254, 'bri': 254, 'transitiontime': 100}
    }
    settings = light_settings.get(emotion_category, {})
    lights = bridge.get_light_objects('id')

    try:
        if current_emotion_category != emotion_category:
            stop_current_players()
            for light_id in lights:
                bridge.set_light(light_id, {'on': True, **settings})
            current_emotion_category = emotion_category
            play_random_song(emotion_category)
            time.sleep(50)  
    except Exception as e:
        logging.error(f"Error while setting light based on emotion: {e}")

def check_emotion_buffer(emotion_category):
    emotion_buffer.append(emotion_category)
    most_common_emotion = max(set(emotion_buffer), key=emotion_buffer.count)
    if emotion_buffer.count(most_common_emotion) >= buffer_threshold:
        return most_common_emotion
    return None

@app.route('/receive_emotion', methods=['POST'])
def receive_emotion():
    try:
        data = request.json
        face_api_data = data.get('face_api_data', {})
        #logging.info(f"Received emotion data: {face_api_data}")
        affectiva_data = data.get('affectiva_data', {})
        #logging.info(f"Received emotion data: {affectiva_data}")

        emotion_scores = {
            'happiness': face_api_data.get('Face API_happy', 0) + affectiva_data.get('Affectiva_joy', 0),
            'sadness': face_api_data.get('Face API_sad', 0) + affectiva_data.get('Affectiva_sadness', 0),
            'anger': face_api_data.get('Face API_angry', 0) + affectiva_data.get('Affectiva_anger', 0),
            'fear': face_api_data.get('Face API_fearful', 0) + affectiva_data.get('Affectiva_fear', 0),
            'disgust': face_api_data.get('Face API_disgusted', 0) + affectiva_data.get('Affectiva_disgust', 0),
            'surprise': face_api_data.get('Face API_surprised', 0) + affectiva_data.get('Affectiva_surprise', 0),
            'neutral': face_api_data.get('Face API_neutral', 0),
            'contempt': affectiva_data.get('Affectiva_contempt', 0)
        }

        predominant_emotion = determine_predominant_emotion(emotion_scores)
        emotion_category = categorize_emotion(predominant_emotion)
        logging.info(f"Predominant emotion: {predominant_emotion}, category: {emotion_category}")

       
        with update_lock:
            consistent_emotion = check_emotion_buffer(emotion_category)
            if consistent_emotion and consistent_emotion != current_emotion_category:
                threading.Thread(target=set_light_based_on_emotion, args=(consistent_emotion,)).start()
                

        append_to_csv(emotion_scores, predominant_emotion, emotion_category)
        emotion_history.append(emotion_category)

        return jsonify({'status': 'success', 'emotion': predominant_emotion, 'emotion_category': emotion_category})
    except Exception as e:
        logging.error(f"Error while receiving emotion: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        stop_current_players()
        logging.info("Program terminated by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        stop_current_players()
        logging.info("Program terminated.")
