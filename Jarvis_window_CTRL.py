# win_assistant.py
# Windows Control Assistant (CMD) — no third-party libs required.
# Run: python win_assistant.py

import os
import sys
import shlex
import ctypes
import subprocess
import time
from datetime import datetime
import subprocess

def open(app_name: str):
    """
    Open a Windows application by name.
    Example: open("notepad"), open("calc")
    """
    try:
        subprocess.Popen(app_name, shell=True)
        print(f"[+] Opening {app_name}...")
    except Exception as e:
        print(f"[x] Error opening {app_name}: {e}")

def close(app_name: str):
    """
    Close an application by process name.
    Example: close("notepad"), close("calc")
    """
    try:
        os.system(f"taskkill /f /im {app_name}.exe")
        print(f"[+] Closed {app_name}")
    except Exception as e:
        print(f"[x] Error closing {app_name}: {e}")

def folder_file(path: str):
    """
    Open a folder or file from its path.
    Example: folder_file(r'C:\\Users\\YourName\\Documents')
    """
    try:
        os.startfile(path)
        print(f"[+] Opened {path}")
    except Exception as e:
        print(f"[x] Error opening {path}: {e}")

IS_WIN = os.name == "nt"
if not IS_WIN:
    print("This assistant is Windows-only.")
    sys.exit(1)

# ---------------------------
# Utilities
# ---------------------------
def run(cmd, shell=False):
    """Run a command and return (code, out, err)."""
    try:
        if shell:
            p = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        else:
            p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, shell=False)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def ps(powershell_script):
    """Run a PowerShell script and return (code, out, err)."""
    return run(f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{powershell_script}"', shell=True)

def info(msg): print(f"[i] {msg}")
def ok(msg):   print(f"[✓] {msg}")
def err(msg):  print(f"[x] {msg}")

# ---------------------------
# Volume control (via key-simulation)
# ---------------------------
# Virtual-Key codes
VK_VOLUME_MUTE  = 0xAD
VK_VOLUME_DOWN  = 0xAE
VK_VOLUME_UP    = 0xAF

# Keyevent via ctypes
user32 = ctypes.WinDLL("user32", use_last_error=True)

def _keybd_event(vk):
    # key down
    user32.keybd_event(vk, 0, 0, 0)
    # key up
    user32.keybd_event(vk, 0, 2, 0)

def vol_mute():
    _keybd_event(VK_VOLUME_MUTE)
    ok("Toggled mute")

def vol_change(steps, up=True, delay=0.01):
    vk = VK_VOLUME_UP if up else VK_VOLUME_DOWN
    for _ in range(max(0, steps)):
        _keybd_event(vk)
        time.sleep(delay)
    ok(f"Volume {'up' if up else 'down'} ({steps} steps)")

def vol_set(percent: int):
    """
    Approximate set by resetting down a lot, then stepping up.
    1 press ≈ ~2% on many systems; your mileage may vary.
    """
    percent = max(0, min(100, percent))
    # push volume to 0 via many downs
    vol_change(60, up=False, delay=0.005)
    # step up to requested level
    steps = round(percent / 2.0)
    vol_change(steps, up=True, delay=0.005)
    ok(f"Volume set to ~{percent}% (approx)")

# ---------------------------
# Brightness control (PowerShell WMI)
# ---------------------------
def brightness_set(percent: int):
    percent = max(0, min(100, percent))
    code, out, e = ps(f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{percent})")
    if code == 0:
        ok(f"Brightness set to {percent}%")
    else:
        err("Failed to set brightness (external monitor may not support WMI). Try Windows Settings.")

def brightness_get():
    code, out, e = ps("(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness")
    if code == 0 and out.strip():
        ok(f"Brightness: {out.strip()}%")
    else:
        err("Could not read brightness.")

# ---------------------------
# Open/Kill/Run
# ---------------------------
def open_item(target: str):
    # Use start (requires shell=True). If path has spaces, quote it.
    code, out, e = run(f'start "" "{target}"', shell=True)
    if code == 0:
        ok(f"Opened: {target}")
    else:
        err(e or f"Failed to open {target}")

def run_cmdline(cmdline: str):
    code, out, e = run(cmdline, shell=True)
    print(out)
    if code != 0:
        err(e or "Command failed")

def list_processes(filter_name: str = ""):
    code, out, e = run("tasklist", shell=True)
    if code != 0:
        err(e or "Failed to list processes")
        return
    if filter_name:
        lines = [ln for ln in out.splitlines() if filter_name.lower() in ln.lower()]
        print("\n".join(lines) if lines else "No matching processes.")
    else:
        print(out)

def kill_process(name_or_pid: str, force=False):
    # Decide if numeric PID or image name
    if name_or_pid.isdigit():
        cmd = f"taskkill /PID {name_or_pid} {'/F' if force else ''}"
    else:
        cmd = f"taskkill /IM {name_or_pid} {'/F' if force else ''}"
    code, out, e = run(cmd, shell=True)
    if code == 0:
        ok(out or f"Killed {name_or_pid}")
    else:
        err(e or out or "Failed to kill")

# ---------------------------
# Files, Explorer, Search
# ---------------------------
def open_explorer(path="."):
    code, out, e = run(f'explorer "{os.path.abspath(path)}"', shell=True)
    if code == 0:
        ok(f"Explorer opened: {os.path.abspath(path)}")
    else:
        err(e or "Failed to open Explorer")

def search_files(root: str, pattern: str):
    # Use PowerShell Get-ChildItem for globbing recursively
    code, out, e = ps(f'Get-ChildItem -Path "{root}" -Recurse -Filter "{pattern}" | Select-Object -ExpandProperty FullName')
    if code == 0:
        if out.strip():
            print(out)
            ok("Search complete")
        else:
            info("No matches found.")
    else:
        err(e or "Search failed")

# ---------------------------
# Wi-Fi & Network
# ---------------------------
def wifi_list():
    code, out, e = run("netsh wlan show networks", shell=True)
    print(out if out else e)

def wifi_connect(ssid: str, key: str):
    # Create temp profile via PowerShell NetConnectionProfile? Simpler: netsh WLAN add profile requires XML,
    # so here: use 'netsh wlan connect name=<profile>' if profile exists.
    # As fallback, try: netsh wlan set hostednetwork / netsh wlan connect ssid
    # Most robust requires a profile already saved. We'll try connect by name (existing profile).
    code, out, e = run(f'netsh wlan connect name="{ssid}"', shell=True)
    if code == 0:
        ok(f"Connecting to '{ssid}' (profile must exist).")
    else:
        err("Windows needs a saved profile to connect by name.\n"
            "Connect once via GUI, then this command will work.\n"
            f"Error: {e or out}")

def wifi_status():
    code, out, e = run("netsh wlan show interfaces", shell=True)
    print(out if out else e)

def net_ipconfig():
    code, out, e = run("ipconfig /all", shell=True)
    print(out if out else e)

# ---------------------------
# Power (shutdown/restart/sleep/lock)
# ---------------------------
def power_shutdown(minutes=0):
    code, out, e = run(f"shutdown /s /t {int(minutes)*60}", shell=True)
    if code == 0: ok(f"System will shutdown in {minutes} min (0 = now).")
    else: err(e or out)

def power_restart(minutes=0):
    code, out, e = run(f"shutdown /r /t {int(minutes)*60}", shell=True)
    if code == 0: ok(f"System will restart in {minutes} min.")
    else: err(e or out)

def power_abort():
    code, out, e = run("shutdown /a", shell=True)
    if code == 0: ok("Shutdown/Restart aborted.")
    else: err(e or out)

def power_sleep():
    # Request suspend
    code, out, e = ps("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    if code == 0: ok("Sleep requested.")
    else: err(e or out)

def power_lock():
    code, out, e = run("rundll32.exe user32.dll,LockWorkStation", shell=True)
    if code == 0: ok("Locked.")
    else: err(e or out)

# ---------------------------
# Clipboard & Speak
# ---------------------------
def clip_set(text: str):
    code, out, e = ps(f'Set-Clipboard -Value @\'\n{text}\n\'@')
    if code == 0: ok("Copied to clipboard.")
    else: err(e or out)

def clip_get():
    code, out, e = ps("Get-Clipboard")
    if code == 0:
        print(out)
        ok("Clipboard read.")
    else:
        err(e or out)

def say(text: str):
    # SAPI.SpVoice
    code, out, e = ps(f"""$speak = New-Object -ComObject SAPI.SpVoice; $speak.Speak("{text}")""")

    if code == 0: ok("Spoken.")
    else: err(e or out)

# ---------------------------
# System info
# ---------------------------
def sysinfo():
    code, out, e = run("systeminfo", shell=True)
    print(out if out else e)

def whoami():
    code, out, e = run("whoami", shell=True)
    print(out if out else e)

def time_now():
    now = datetime.now()
    ok(now.strftime("%Y-%m-%d %H:%M:%S"))

# ---------------------------
# Scheduling via schtasks
# ---------------------------
def schedule_once(task_name: str, time_hhmm: str, cmdline: str):
    """
    Create a one-time scheduled task at HH:MM today (24h). Runs under current user.
    Example:
      schedule_once "MyTask" 21:30 "notepad.exe"
    """
    # Build command that starts minimized in cmd
    cmd = f'cmd.exe /c {cmdline}'
    code, out, e = run(
        f'schtasks /Create /SC ONCE /TN "{task_name}" /TR "{cmd}" /ST {time_hhmm} /RL HIGHEST /F',
        shell=True
    )
    if code == 0: ok(f"Task '{task_name}' scheduled at {time_hhmm}.")
    else: err(e or out)

def schedule_delete(task_name: str):
    code, out, e = run(f'schtasks /Delete /TN "{task_name}" /F', shell=True)
    if code == 0: ok(f"Task '{task_name}' deleted.")
    else: err(e or out)

def schedule_list():
    code, out, e = run("schtasks", shell=True)
    print(out if out else e)

# ---------------------------
# Help text
# ---------------------------
HELP = r"""
Windows Control Assistant — commands (type: help to see this)

General:
  help                          Show this help
  exit / quit                   Exit assistant
  time                          Show current time
  sysinfo                       System information
  whoami                        Current user

Open / Run / Processes:
  open <path|url|app>           Open file/folder/app/URL (Explorer or default app)
  explorer [path]               Open Explorer at path (default: current dir)
  run <command>                 Run a raw command (PowerShell/cmd)
  pslist [name]                 List processes (optionally filter by name)
  kill <name|pid> [force]       Kill process by image name or PID (add 'force' to force)

Audio:
  vol up [n]                    Volume up by n steps (default 5)
  vol down [n]                  Volume down by n steps (default 5)
  vol mute                      Toggle mute
  vol set <0-100>               Approx set volume to percentage

Display:
  bright get                    Show current brightness
  bright set <0-100>            Set brightness percentage (WMI internal display only)

Network:
  ip                            ipconfig /all
  wifi list                     List nearby Wi-Fi networks
  wifi status                   Current Wi-Fi interface status
  wifi connect <ssid>           Connect to saved Wi-Fi profile (must exist)

Power:
  shutdown [minutes]            Shutdown after minutes (0 = now)
  restart [minutes]             Restart after minutes
  abort                         Abort pending shutdown/restart
  sleep                         Sleep now
  lock                          Lock workstation

Clipboard & Speech:
  clip set <text>               Copy text to clipboard
  clip get                      Print clipboard text
  say <text>                    Text-to-speech (SAPI)

Files:
  search <root> <pattern>       Recursive search (e.g., search C:\ *.pdf)

Scheduler:
  task list                     List tasks
  task add <name> <HH:MM> <cmd> Create one-time task today (24h)
  task del <name>               Delete a task
"""

# ---------------------------
# Parser/Dispatcher
# ---------------------------
def dispatch(raw: str):
    raw = raw.strip()
    if not raw:
        return

    parts = shlex.split(raw)
    cmd = parts[0].lower()
    args = parts[1:]

    # General
    if cmd in ("help", "?"):
        print(HELP); return
    if cmd in ("exit", "quit"):
        print("Bye!"); sys.exit(0)
    if cmd == "time":
        time_now(); return
    if cmd == "sysinfo":
        sysinfo(); return
    if cmd == "whoami":
        whoami(); return

    # Open/Run/Processes
    if cmd == "open" and args:
        open_item(" ".join(args)); return
    if cmd == "explorer":
        path = args[0] if args else "."
        open_explorer(path); return
    if cmd == "run" and args:
        run_cmdline(" ".join(args)); return
    if cmd == "pslist":
        filt = args[0] if args else ""
        list_processes(filt); return
    if cmd == "kill" and args:
        name_pid = args[0]
        force = (len(args) > 1 and args[1].lower() == "force")
        kill_process(name_pid, force); return

    # Audio
    if cmd == "vol" and args:
        sub = args[0].lower()
        if sub == "up":
            steps = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5
            vol_change(steps, up=True); return
        if sub == "down":
            steps = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5
            vol_change(steps, up=False); return
        if sub == "mute":
            vol_mute(); return
        if sub == "set" and len(args) > 1 and args[1].isdigit():
            vol_set(int(args[1])); return

    # Brightness
    if cmd == "bright" and args:
        sub = args[0].lower()
        if sub == "get":
            brightness_get(); return
        if sub == "set" and len(args) > 1 and args[1].isdigit():
            brightness_set(int(args[1])); return

    # Network
    if cmd == "ip":
        net_ipconfig(); return
    if cmd == "wifi" and args:
        sub = args[0].lower()
        if sub == "list":
            wifi_list(); return
        if sub == "status":
            wifi_status(); return
        if sub == "connect" and len(args) > 1:
            ssid = " ".join(args[1:])
            wifi_connect(ssid, key=""); return

    # Power
    if cmd == "shutdown":
        mins = int(args[0]) if args and args[0].isdigit() else 0
        power_shutdown(mins); return
    if cmd == "restart":
        mins = int(args[0]) if args and args[0].isdigit() else 0
        power_restart(mins); return
    if cmd == "abort":
        power_abort(); return
    if cmd == "sleep":
        power_sleep(); return
    if cmd == "lock":
        power_lock(); return

    # Clipboard & Speech
    if cmd == "clip" and args:
        sub = args[0].lower()
        if sub == "set" and len(args) > 1:
            clip_set(" ".join(args[1:])); return
        if sub == "get":
            clip_get(); return
    if cmd == "say" and args:
        say(" ".join(args)); return

    # Files
    if cmd == "search" and len(args) >= 2:
        root = args[0]
        pattern = " ".join(args[1:])
        search_files(root, pattern); return

    # Scheduler
    if cmd == "task" and args:
        sub = args[0].lower()
        if sub == "list":
            schedule_list(); return
        if sub == "add" and len(args) >= 4:
            name = args[1]
            hhmm = args[2]
            cmdline = " ".join(args[3:])
            schedule_once(name, hhmm, cmdline); return
        if sub == "del" and len(args) >= 2:
            name = args[1]
            schedule_delete(name); return

    err("Unknown or incomplete command. Type: help")

# ---------------------------
# Main Loop
# ---------------------------
def main():
    print("=== Windows Control Assistant (CMD) ===")
    print("Type 'help' to see commands. Type 'exit' to quit.")
    while True:
        try:
            line = input("win> ")
            dispatch(line)
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        except Exception as e:
            err(f"Unhandled error: {e}")
