import webbrowser
import musicLibrary

def play_song(command):
    command = command.lower()
    found = False
    for song in musicLibrary.music:
        if song in command:
            webbrowser.open(musicLibrary.music[song])
            print(f"Playing: {song}")
            found = True
            break
    if not found:
        print("Sorry, I couldn't find that song in your library.")

# TEST COMMAND:
user_command = input("Say your command: ")  # Simulate voice input
play_song(user_command)
