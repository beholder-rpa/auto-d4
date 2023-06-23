#from win32gui import GetWindowText, GetForegroundWindow
from threading import Thread, Lock
from PIL import Image
import dxcam
import simpleaudio as sa
import pytesseract
import numpy as np
import math
import os
import cv2
from time import sleep
from datetime import datetime
import re
import random
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from colorama import Style, Fore, init as colorama_init
import concurrent.futures
import easyocr

alert = sa.WaveObject.from_wave_file(
    os.path.dirname(__file__) + "\\sounds\\fanfare.wav"
)
error = sa.WaveObject.from_wave_file(os.path.dirname(__file__) + "\\sounds\\error.wav")
keyboard = KeyboardController()
mouse = MouseController()

settings =  lambda **kwargs: type("Settings", (), kwargs)()
settings.debug = False
settings.play_low_health_sound = True
settings.target_fps = 6

def auto_heal():
    keyboard.tap('q')

def process_frame(frame, target_fps):
    global settings

    if settings.debug:
        with Image.fromarray(frame) as img:
            img.save("./debug.jpg")

def main(args):
    global settings
    global reader

    colorama_init()
    settings.debug = args.debug

    reader = easyocr.Reader(['en'], gpu=args.use_cuda) # there's also the detect_network argument?

    print(dxcam.device_info())
    print(dxcam.output_info())

    camera = dxcam.create(output_idx=0, output_color="BGR")
    camera.start(target_fps=args.target_fps, video_mode=False)

    print(f"{Fore.LIGHTMAGENTA_EX}Starting auto-d4...{Style.RESET_ALL}")
    print(
        f"\t{Fore.LIGHTYELLOW_EX}Target FPS: {args.target_fps} ({60/args.target_fps/60:.2f} seconds per frame){Style.RESET_ALL}"
    )
    if args.debug:
        print(f"\t{Fore.LIGHTGREEN_EX}Debugging mode enabled{Style.RESET_ALL}")
    print(f"Press Ctrl+C to exit...")

    while True:
        try:
            frame = camera.get_latest_frame()
            process_frame(
                frame,
                target_fps=args.target_fps,
            )
        except KeyboardInterrupt:
            print("Exiting...")
            try:
                camera.stop()
            except:
                pass
            exit()
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    from modules import cmd_args
    args, _ = cmd_args.parser.parse_known_args()
    main(args)
