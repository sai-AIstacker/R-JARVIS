# agent.py

# इस फाइल में 'object_detection.py' को integrate किया गया है।

import subprocess
import sys
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)
from Jarvis_prompts import behavior_prompts, Reply_prompts
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open, close, folder_file, main
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool,
    press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
)
from youtube_tool import play_youtube_video
from whatsapp_tool import send_whatsapp_message
from volume_tool import control_volume, control_brightness

# नया import: हमारी नई object_detection.py फ़ाइल से फ़ंक्शन ला रहे हैं।
from object_detection import live_object_detection

# --- Manually add all API keys/IDs here ---
LIVEKIT_API_KEY = 
LIVEKIT_API_SECRET = 
LIVEKIT_URL = 

GOOGLE_API_KEY = 
GOOGLE_SEARCH_API_KEY = 
SEARCH_ENGINE_ID = 
OPENWEATHER_API_KEY = 

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=behavior_prompts,
            tools=[
                google_search,
                get_current_datetime,
                get_weather,
                open,
                close,
                folder_file,
                Play_file,
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                press_hotkey_tool,
                control_volume_tool,
                swipe_gesture_tool,
                play_youtube_video,
                send_whatsapp_message,
                control_volume,
                control_brightness,
                # नया टूल यहाँ जोड़ दिया गया है ताकि Jarvis इसे इस्तेमाल कर सके।
                live_object_detection
            ]
        )

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            api_key=GOOGLE_API_KEY,
            voice="Charon"  # अगर error आए तो इस लाइन को हटा दें
        )
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True
        ),
    )
    await ctx.connect()
    await session.generate_reply(
        instructions=Reply_prompts
    )

import os
def cmd_process():
    choice = input("1 for cmd process 2 for file operations")
    if(choice == "1"):
        main()
    elif(choice == "2"):
        ch = input("if to open app enter 'open app' appname")
        if("open app" in ch):
            app_name = ch.split("open app", 1)[1].strip()
            open(app_name)
        elif("close app" in ch):
            app_name = ch.split("close app", 1)[1].strip()
            close(app_name)
        elif("folder" in ch):
            folder_name = ch.split("folder", 1)[1].strip()
            folder_file(folder_name)

if __name__ == "__main__":

    option = input("What do you want to do with R-Jarvis? press 1)Animation 2)Windows Process 3)Object Detection")
    if "1" in option:
        # Animation window को auto-launch करें (jarvis_animation.py)
        try:
            subprocess.Popen([sys.executable, "jarvis_animation.py"])
        except Exception as e:
            print("Animation window launch error:", e)
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
            # webcam को बंद करें।
    elif "2" in option:
        cmd_process()
    elif "3" in option:
        live_object_detection()
