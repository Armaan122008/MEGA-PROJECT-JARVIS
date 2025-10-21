import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import wikipedia
import pytube
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import sys
import time

# Add the path to the musicLibrary directory
sys.path.append("path_to_musicLibrary_directory")
import musicLibrary

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# API keys
NEWS_API_KEY = "dd63574a7d5943269ae89b984d36a767"
WEATHER_API_KEY = "1817ee74782fac6fd1629ed940705b59"

# Global list to store reminders
reminders = []

def speak(text):
    """Speak the given text."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to the user's voice input and return the recognized text."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Can you repeat?")
        except sr.RequestError:
            speak("There was an issue with the speech recognition service.")
        except sr.WaitTimeoutError:
            speak("You were silent for too long. Please try again.")
    return None

def processCommand(c):
    """Process the user's command and perform the corresponding action."""
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")
        speak("Opening Google")

    elif "open snapchat" in c:
        webbrowser.open("https://snapchat.com")
        speak("Opening Snapchat")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")

    elif "weather in" in c:
        city = c.split("in")[-1].strip()
        get_weather(city)

    elif "add song" in c:
        add_song_interactively()

    elif "play" in c:
        play_song(c)

    elif "news" in c:
        fetch_news()

    elif "joke" in c:
        tell_joke()

    elif "set reminder" in c:
        set_reminder()

    elif "show reminders" in c:
        show_reminders()

    elif "increase volume" in c:
        increase_volume()

    elif "decrease volume" in c or "slow down volume" in c:
        decrease_volume()

    elif "search wikipedia for" in c:
        query = c.split("for")[-1].strip()
        search_wikipedia(query)

    elif "play video" in c:
        query = c.split("video")[-1].strip()
        play_youtube_video(query)

    else:
        speak("Sorry, I didn't understand that. Can you repeat?")

def get_weather(city):
    """Fetch and speak the weather for the given city."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            speak(f"The current weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
        elif response.status_code == 404:
            speak(f"Sorry, I couldn't find weather information for {city}.")
        else:
            speak("Sorry, I couldn't fetch the weather information.")
    except requests.exceptions.RequestException:
        speak("There was a network error while fetching the weather.")

def add_song_interactively():
    """Add a song to the music library by interacting with the user."""
    speak("Please say the song name.")
    song_name = listen()
    if song_name:
        speak("Please say the song URL.")
        song_url = listen()
        if song_url:
            add_song(song_name, song_url)

def add_song(song_name, song_url):
    """Add a song to the music library."""
    if song_name in musicLibrary.music:
        speak(f"{song_name} is already in the library.")
    else:
        musicLibrary.music[song_name] = song_url
        speak(f"{song_name} has been added to your library.")

def play_song(command):
    """Play a song from the library or search YouTube."""
    found = False
    for song in musicLibrary.music:
        if song in command:
            webbrowser.open(musicLibrary.music[song])
            speak(f"Playing {song}")
            found = True
            break
    if not found:
        speak("I couldn't find that song in your library. Searching YouTube instead.")
        play_youtube_video(command.replace("play", "").strip())

def fetch_news():
    """Fetch and speak the top news headlines."""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                speak("Here are the top headlines:")
                for article in articles[:5]:
                    title = article.get('title', 'No title')
                    speak(title)
            else:
                speak("Sorry, I couldn't find any news articles.")
        else:
            speak("Couldn't fetch the news right now.")
    except requests.exceptions.RequestException:
        speak("There was a network error while fetching the news.")

def tell_joke():
    """Fetch and speak a random joke."""
    try:
        url = "https://official-joke-api.appspot.com/random_joke"
        response = requests.get(url)
        if response.status_code == 200:
            joke = response.json()
            speak(joke["setup"])
            time.sleep(1)
            speak(joke["punchline"])
        else:
            speak("Sorry, I couldn't fetch a joke right now.")
    except requests.exceptions.RequestException:
        speak("There was a network error while fetching the joke.")

def set_reminder():
    """Set a reminder."""
    speak("What should I remind you about?")
    reminder = listen()
    if reminder:
        reminders.append(reminder)
        speak(f"Reminder set: {reminder}.")

def show_reminders():
    """Show all reminders."""
    if reminders:
        speak("Here are your reminders:")
        for i, reminder in enumerate(reminders, 1):
            speak(f"{i}. {reminder}")
    else:
        speak("You have no reminders.")

def increase_volume():
    """Increase the system volume."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(current_volume + 0.1, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume increased.")
    except Exception:
        speak("An error occurred while increasing the volume.")

def decrease_volume():
    """Decrease the system volume."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.1, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume decreased.")
    except Exception:
        speak("An error occurred while decreasing the volume.")

def search_wikipedia(query):
    """Search Wikipedia and speak the summary."""
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Your query is too ambiguous. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find anything on Wikipedia for that query.")

def play_youtube_video(query):
    """Search YouTube and play the first video result."""
    try:
        speak(f"Searching YouTube for {query}.")
        yt = pytube.Search(query)
        if yt.results:
            video = yt.results[0]
            webbrowser.open(video.watch_url)
            speak(f"Playing {query} on YouTube.")
        else:
            speak("No results found on YouTube.")
    except Exception:
        speak("An error occurred while searching YouTube.")

if __name__ == "__main__":
    speak("Initializing Jarvis...")
    while True:
        speak("Say 'hello' to activate.")
        word = listen()
        if word and word.lower() == "hello":
            speak("Yes, what can I do?")
            command = listen()
            if command:
                processCommand(command)




