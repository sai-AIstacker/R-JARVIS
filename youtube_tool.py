# youtube_tool.py
import pywhatkit as kit

def play_youtube_video(query: str):
    """
    Plays a YouTube video based on a voice query.
    Example: 'play despacito on youtube'
    """
    try:
        kit.playonyt(query)
        print(f"Playing YouTube video for: {query}")
    except Exception as e:
        print("Error playing YouTube video:", e)