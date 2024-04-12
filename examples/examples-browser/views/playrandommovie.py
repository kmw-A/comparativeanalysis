# import vlc
# import time
# import random
# import os

# # Specify the path to the directory containing the video files
# video_directory = '/path/to/video/folder'

# # List all video files in the directory
# video_files = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if f.endswith(('.mp4', '.avi', '.mov'))]

# # Randomly shuffle the list of video files
# random.shuffle(video_files)

# # Function to play a video
# def play_video(video_path):
#     player = vlc.MediaPlayer(video_path)
#     player.play()
#     time.sleep(1)  # Wait for it to start
#     while player.is_playing():
#         time.sleep(1)  # Let the video play
#     player.stop()

# # Play each video in the shuffled list
# for video in video_files:
#     print(f"Playing {video}")
#     play_video(video)


# import vlc
# import time

# def play_movie(path, pause_times, stop_time):

#     player = vlc.Instance()

#     media_player = player.media_player_new()

#     media = player.media_new(path)

#     media_player.set_media(media)

#     media_player.play()
#     time.sleep(1)  

#     for pause_time in pause_times:

#         pause_time_ms = (pause_time[0] * 60 + pause_time[1]) * 1000

#         while media_player.get_time() < pause_time_ms:
#             time.sleep(1)

#         media_player.pause()

#         input("Paused at {:02d}:{:02d}. Type 'continue' and press Enter to continue: ".format(*pause_time))

#         media_player.play()

#     stop_time_ms = (stop_time[0] * 60 + stop_time[1]) * 1000
#     while media_player.get_time() < stop_time_ms:
#         time.sleep(1)

#     media_player.stop()

# if __name__ == "__main__":

#     movie_path = "/Users/kevinfred/Downloads/VideoPlaylist/Second_set_ABC.mp4"

#     pause_times = [(2, 28), (2, 44)]

#     stop_time = (2, 44)

#     play_movie(movie_path, pause_times, stop_time)
# import vlc
# import time

# def play_movie(path, pause_times, stop_time):
#     player = vlc.Instance()
#     media_player = player.media_player_new()
#     media = player.media_new(path)
#     media_player.set_media(media)

#     # Set fullscreen mode (optional)
#     media_player.set_fullscreen(True)

#     if media_player.play() == -1:
#         print("Error: Cannot play the media file.")
#         return

#     while media_player.get_state() != vlc.State.Playing:
#         time.sleep(1)

#     for pause_time in pause_times:
#         pause_time_ms = (pause_time[0] * 60 + pause_time[1]) * 1000
#         while media_player.get_time() < pause_time_ms:
#             time.sleep(1)
#         media_player.pause()
#         input("Paused at {:02d}:{:02d}. Press Enter to continue: ".format(*pause_time))
#         media_player.play()

#     stop_time_ms = (stop_time[0] * 60 + stop_time[1]) * 1000
#     while media_player.get_time() < stop_time_ms:
#         time.sleep(1)

#     media_player.stop()
#     media_player.release()

# if __name__ == "__main__":
#     movie_path = "/Users/kevinfred/Downloads/VideoPlaylist/Second_set_ABC.mp4"
#     pause_times = [(2, 28), (2, 44)]
#     stop_time = (2, 44)
#     play_movie(movie_path, pause_times, stop_time)



# importing vlc module
import vlc
 
# importing time module
import time
 
 
# creating vlc media player object
media_player = vlc.MediaPlayer()
 
# media object
media = vlc.Media("/Users/kevinfred/Downloads/VideoPlaylist/Second_set_ABC.mp4")
 
# setting media to the media player
media_player.set_media(media)
 
 
# start playing video
media_player.play()
 
# wait so the video can be played for 5 seconds
# irrespective for length of video
time.sleep(5)