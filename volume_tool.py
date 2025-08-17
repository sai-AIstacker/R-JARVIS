from livekit.agents import function_tool

# ----------- वॉल्यूम कंट्रोल (Windows) -----------
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

@function_tool
async def control_volume(action: str):
    """
    वॉल्यूम को 'up', 'down', 'mute', या 'unmute' करें।
    """
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    if action == "up":
        volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
        return "वॉल्यूम बढ़ा दिया गया।"
    elif action == "down":
        volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
        return "वॉल्यूम घटा दिया गया।"
    elif action == "mute":
        volume.SetMute(1, None)
        return "वॉल्यूम म्यूट कर दिया गया।"
    elif action == "unmute":
        volume.SetMute(0, None)
        return "वॉल्यूम अनम्यूट कर दिया गया।"
    else:
        return "Unknown action."

# ----------- ब्राइटनेस कंट्रोल (Windows) -----------
import screen_brightness_control as sbc

@function_tool
async def control_brightness(action: str, value: int = 10):
    """
    ब्राइटनेस को 'up', 'down', या 'set' करें।
    """
    current = sbc.get_brightness(display=0)
    if action == "up":
        sbc.set_brightness(min(current[0] + value, 100), display=0)
        return f"ब्राइटनेस {value}% बढ़ा दी गई।"
    elif action == "down":
        sbc.set_brightness(max(current[0] - value, 0), display=0)
        return f"ब्राइटनेस {value}% घटा दी गई।"
    elif action == "set":
        sbc.set_brightness(value, display=0)
        return f"ब्राइटनेस {value}% पर सेट कर दी गई।"
    else:
        return "Unknown action."