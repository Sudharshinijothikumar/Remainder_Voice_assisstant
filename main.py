import speech_recognition as sr
import pyttsx3
import json
import os
import re
import difflib
from datetime import datetime, timedelta
from word2number import w2n
import calendar

REMINDER_FILE = "reminders.json"

voiceEngine = pyttsx3.init('sapi5')
voices = voiceEngine.getProperty('voices')
voiceEngine.setProperty('voice', voices[0].id)
recognizer = sr.Recognizer()

def speak(text):
    voiceEngine.say(text)
    voiceEngine.runAndWait()

def listen(prompt=None, retries=3):
    if prompt:
        speak(prompt)
    for _ in range(retries):
        with sr.Microphone() as source:
            print("Listening... Speak now.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command.lower()
            except sr.WaitTimeoutError:
                speak("You were silent. Please try again.")
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
            except sr.RequestError:
                speak("There was a problem reaching the recognition service.")
    return ""

def parse_spoken_time(spoken_time):
    spoken_time = spoken_time.lower().replace('.', '').replace("o'clock", '')
    spoken_time = spoken_time.replace("a m", "am").replace("p m", "pm").replace(':', ' ')
    spoken_time = re.sub(r'\s+', ' ', spoken_time).strip()

    tokens = spoken_time.split()
    converted_tokens = []
    for t in tokens:
        if t.isalpha():
            try:
                num = w2n.word_to_num(t)
                converted_tokens.append(str(num))
            except ValueError:
                converted_tokens.append(t)
        else:
            converted_tokens.append(t)
    spoken_time = ' '.join(converted_tokens)

    match = re.search(r"(\d{1,2})(\s+(\d{1,2}))?\s*(am|pm)?", spoken_time)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(3)) if match.group(3) else 0
        am_pm = match.group(4)
        if am_pm == "pm" and hour != 12:
            hour += 12
        elif am_pm == "am" and hour == 12:
            hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
    return None

def parse_spoken_date(spoken_date):
    spoken_date = spoken_date.lower().replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
    tokens = spoken_date.split()
    month = None
    date = None
    for token in tokens:
        try:
            num = w2n.word_to_num(token)
            if not date:
                date = num
        except ValueError:
            if token.capitalize() in calendar.month_name:
                month = token.capitalize()
    if month and date and 1 <= date <= 31:
        return month, date
    return None, None

def parse_time_and_date(month, date, hour, minute):
    try:
        dt = datetime.strptime(f"{datetime.now().year} {month} {date} {hour:02}:{minute:02}", "%Y %B %d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return None

def load_reminders():
    return json.load(open(REMINDER_FILE)) if os.path.exists(REMINDER_FILE) else {}

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

def add_reminder():
    content = listen("What is the reminder about?")
    if not content:
        speak("Reminder content not received.")
        return

    while True:
        date_input = listen("Say the date like 'June 2' or 'August 11'")
        month, date = parse_spoken_date(date_input)
        if not month or not date:
            speak("Could not understand the date.")
            continue

        time_spoken = listen("What time? Say like '3 PM' or '3 30 PM'")
        parsed_time = parse_spoken_time(time_spoken)
        if not parsed_time:
            speak("Could not understand the time.")
            continue

        hour, minute = parsed_time
        datetime_key = parse_time_and_date(month, date, hour, minute)
        if not datetime_key:
            speak("Invalid date or time.")
            continue

        # Check if the datetime is in the past
        reminder_time = datetime.strptime(datetime_key, "%Y-%m-%d %H:%M")
        if reminder_time < datetime.now():
            speak("That date and time is already over. Please say another date.")
            continue
        break  # Exit loop if valid future datetime is given

    repeat = listen("Repeat daily, weekly, monthly, yearly or once?").lower()
    matches = difflib.get_close_matches(repeat, ["daily", "weekly", "monthly", "yearly", "once"], n=1, cutoff=0.6)
    repeat = matches[0] if matches else "once"

    reminders = load_reminders()
    if datetime_key in reminders:
        speak("You already have a reminder at that time.")
        return

    speak(f"You said '{content}' on {datetime_key} repeating {repeat}. Say do it or add it to confirm.")
    confirmation = listen()
    if "do it" in confirmation or "yes" in confirmation or "add it" in confirmation:
        reminders[datetime_key] = {"content": content, "repeat": repeat}
        save_reminders(reminders)
        speak("Reminder saved.")
    else:
        speak("Reminder not saved.")


def view_reminders():
    reminders = load_reminders()
    if not reminders:
        speak("You have no reminders.")
        return
    now = datetime.now()
    upcoming = []
    for time_str, info in reminders.items():
        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        content = info.get("content", "") if isinstance(info, dict) else info
        repeat = info.get("repeat", "once") if isinstance(info, dict) else "once"
        if repeat == "once" and time_obj >= now:
            upcoming.append((time_obj, content, repeat))
        elif repeat == "daily":
            while time_obj < now:
                time_obj += timedelta(days=1)
            upcoming.append((time_obj, content, repeat))
        elif repeat == "weekly":
            while time_obj < now:
                time_obj += timedelta(weeks=1)
            upcoming.append((time_obj, content, repeat))
        elif repeat == "monthly":
            while time_obj < now:
                year = time_obj.year + (time_obj.month // 12)
                month = (time_obj.month % 12) + 1
                day = min(time_obj.day, 28)
                time_obj = time_obj.replace(year=year, month=month, day=day)
            upcoming.append((time_obj, content, repeat))
        elif repeat == "yearly":
            while time_obj < now:
                time_obj = time_obj.replace(year=time_obj.year + 1)
            upcoming.append((time_obj, content, repeat))
    if not upcoming:
        speak("No upcoming reminders.")
        return
    upcoming.sort()
    speak("Here are your upcoming reminders:")
    for time, note, rep in upcoming:
        speak(f"{note} on {time.strftime('%A, %B %d at %I:%M %p')}, repeating {rep}")

def remove_reminder():
    target = listen("What reminder do you want to remove?")
    reminders = load_reminders()
    for k in list(reminders):
        content = reminders[k]["content"] if isinstance(reminders[k], dict) else reminders[k]
        if target.lower() in content.lower():
            speak(f"Found: {content} at {k}. Say 'do it' to confirm.")
            confirmation = listen()
            if "do it" in confirmation or "yes" in confirmation or "remove it" in confirmation:
                del reminders[k]
                save_reminders(reminders)
                speak("Reminder removed.")
                return
    speak("No matching reminder found.")

def wish():
    hour = datetime.now().hour
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your assistant, Laddoo. How can I help you today?")

def main():
    wish()
    while True:
        command = listen("Your command?")
        if "add" in command:
            add_reminder()
        elif "view" in command or "show" in command:
            view_reminders()
        elif "remove" in command or "delete" in command:
            remove_reminder()
        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break
        else:
            speak("Unknown command. Try again.")

if __name__ == "__main__":
    main()
