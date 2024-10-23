import subprocess
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from datetime import datetime
import time
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

# Mapping of spoken application names to their executable names
app_mapping = {
    "google chrome": "google-chrome",
    "firefox": "firefox",
    "terminal": "gnome-terminal",
    "vs code": "code",
    "settings": "gnome-control-center",
    "task manager": "gnome-system-monitor",
}

def speak(text):
    def _speak():
        tts = gTTS(text=text, lang='en')
        filename = "/tmp/temp_audio.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    
    thread = threading.Thread(target=_speak)
    thread.start()

def log_message(message):
    text_area.insert(tk.END, message + "\n")
    text_area.see(tk.END)

def clear_last_message():
    for _ in range(2):  # Loop to delete the last 2 lines
        last_message_index = text_area.index("end-2c linestart")  # Get the index of the second to last line start
        text_area.delete(last_message_index, "end-1c")  # Delete the line from last_message_index to the end of the second last line

def listen_for_command():
    recognizer = sr.Recognizer()
    
    recognizer.energy_threshold = 300  # The quieter the environment the lower the value

    with sr.Microphone() as source:
        speak("Hi.")
        log_message("\n Lunita: Hi, I'm listening.")
        log_message("\n  Listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        clear_last_message() 
        log_message(f"\n You: {command}")
        return command
    
    except sr.UnknownValueError:
        clear_last_message() 
        log_message("\n  Could not understand audio.")
        return ""
    except sr.RequestError as e:
        clear_last_message() 
        log_message(f"\n  Error fetching results; {e}")
        return ""

def return_home():
    log_message("\n Lunita: Okay, returning to home screen...")
    speak("Okay, returning to home screen.")
    subprocess.run(["xdotool", "key", "super+d"])

def lock_screen():
    log_message("\n Lunita: Okay, locking the screen...")
    speak("Okay, locking the screen.")
    subprocess.run(["xdotool", "key", "super+l"])

def empty_trash():
    log_message("\n Lunita: Okay, emptying the trash...")
    speak("Okay, emptying the trash.")
    subprocess.run(["trash-empty"])

def save_idea(idea_text):
    current_datetime = datetime.now()
    filename = f"idea_{current_datetime.strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.expanduser(f"~/Documents/{filename}")
    with open(file_path, "a") as file:
        file.write(idea_text + "\n")
    log_message(f"\n  Idea saved to: {file_path}")
    return file_path

def open_file(file_path):
    subprocess.run(["xdg-open", file_path])

def open_application(app_name):
    if app_name == "files":
        try:
            log_message(f"\n Lunita: Okay, opening 'file manager'...")
            speak(f"Okay, opening file manager.")
            subprocess.Popen(["xdg-open", os.path.expanduser("~/")])
        except FileNotFoundError:
            log_message("\n Lunita: Unable to open file manager.")
            speak("Unable to open file manager.")
    else:
        executable_name = app_mapping.get(app_name)
        if executable_name:
            try:
                log_message(f"\n Lunita: Okay, opening '{app_name}'...")
                speak(f"Okay, opening {app_name}.")
                subprocess.Popen([executable_name])
            except FileNotFoundError:
                log_message(f"\n Lunita: Application '{executable_name}' not found.")
                speak(f"Application {executable_name} not found.")
        else:
            log_message(f"\n Lunita: Application '{app_name}' not found.")
            speak(f"Application {app_name} not found.")

def main():
    while True:
        command = listen_for_command()

        if command.startswith("what's your name"):
            log_message("\n Lunita: My name is Lunita.")
            speak("My name is Lunita.")
            time.sleep(2)

        elif all(word in command for word in ["meaning", "your", "name"]):
            log_message("""\n Lunita: In Spanish, my name 'Lunita' can be interpreted as 'little moon' or 'little Luna'. The word carries a sense of endearment and tenderness, as if referring to something precious and beautiful, much like a cherished moment under a starlit sky.""")
            speak("""In Spanish, my name Lunita can be interpreted as little moon or little Luna. 
                  The word carries a sense of endearment and tenderness, as if referring to something precious and beautiful, 
                  much like a cherished moment under a starlit sky.""")
            time.sleep(20)

        elif command.startswith("goodbye"):
            log_message("\n Lunita: Okay, see you soon!")
            speak("Okay, see you soon!")
            root.after(100, clear_text_area) 
            break

        elif command.startswith("stay there"):
            log_message("\n Lunita: Okay, I'll stay!")
            speak("Okay, I'll stay!")
            break

        elif command.startswith("return home"):
            return_home()
            root.after(1000, clear_text_area) 
            break

        elif command.startswith("lock the"):
            lock_screen()
            root.after(1000, clear_text_area) 
            break

        elif command.startswith("empty"):
            empty_trash()
            root.after(1000, clear_text_area) 
            break

        elif command.startswith("today's idea"):
            idea_text = command[len("today's idea") + 1:]  # Extract text after "today's idea"
            log_message(f"\n Lunita: Okay, saving idea: {idea_text}")
            speak("Okay, saving idea.")
            saved_file_path = save_idea(idea_text)
            open_file(saved_file_path)
            root.after(10000, clear_text_area) 
            break

        elif command.startswith("open "):
            app_name = command[len("open "):]  # Extract app name after "open"
            open_application(app_name)
            root.after(1000, clear_text_area) 
            break

        else:
            log_message("\n Lunita: Command not recognized. Please try again.")
            speak("Please try again.")
            time.sleep(2)

def clear_text_area():
    text_area.delete(1.0, tk.END)
    root.quit()

if __name__ == "__main__":
    # Create a Tkinter window
    root = tk.Tk(className='Lunita')
    root.title("Ubuntu's assistant Lunita")
    root.geometry("1440x480")  # Set window size
    root.configure(bg='#542c74')  # Set background color to purple

    # Disable window resizing
    root.resizable(False, False)

    # Set application icon
    icon_path = "/home/minh/scripts/lunita-icon.png"
    icon = tk.PhotoImage(file=icon_path)
    root.iconphoto(False, icon)

    # Create a frame for text area and image
    frame = tk.Frame(root, bg='#542c74')
    frame.pack(fill=tk.BOTH, expand=True)

    # Create a ScrolledText widget for displaying log messages
    text_area = ScrolledText(frame, wrap=tk.WORD, width=60, font=("Helvetica", 15, "bold"), bg='#542c74', fg='white')
    text_area.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.BOTH, expand=True)

    # Load and display Lunita image
    image_path = "/home/minh/scripts/Lunita3.jpg"
    img = Image.open(image_path)
    img = img.resize((720, 480), Image.ANTIALIAS)  # Resize the image to fit
    img = ImageTk.PhotoImage(img)

    img_label = tk.Label(frame, image=img, bg='#542c74')
    img_label.pack(side=tk.RIGHT, padx=0, pady=5, fill=tk.BOTH, expand=True)

    # Start the main function in a separate thread
    threading.Thread(target=main).start()

    # Run the Tkinter main loop
    root.mainloop()


