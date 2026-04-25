import time
import os

def clear_screen():
    os.system("cls")

def slow_print(text):
    for character in text:
        print(character,end="",flush=True)
        time.sleep(0.02)
    print()

def show_divider():
    print("======================================================")