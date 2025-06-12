# Remainder_Voice_assisstant
Laddoo is a voice-controlled reminder assistant built with Python. It listens to your natural speech to set, view, and remove reminders using simple voice commands. With support for repeating reminders and offline text-to-speech, Laddoo helps you stay organized—hands-free and hassle-free.
# 🗣️ Voice-Based Reminder Assistant - Laddoo

This is a voice-activated reminder system built with Python. It allows users to add, view, and delete reminders using natural speech input. It features text-to-speech (TTS), speech recognition, and persistent reminder storage.

## 🎯 Features

- Voice-controlled reminder creation
- Date and time parsing from natural speech
- Daily, weekly, monthly, and yearly repeating reminders
- Friendly TTS responses via pyttsx3
- Persistent reminders stored in a JSON file

## 🛠️ Requirements

- Python 3.7+
- Microphone access

Install dependencies:

```bash
pip install -r requirements.txt
🚀 How to Run
bash
Copy
Edit
python main.py
Then follow the voice prompts to add, view, or remove reminders.

📁 Project Structure
bash
Copy
Edit
main.py             # Core assistant logic
reminders.json      # Saved reminders (auto-created)
requirements.txt    # Dependency list
README.md           # This file


🤖 Voice Engine
Uses:

speech_recognition (Google Speech API)

pyttsx3 for offline TTS

word2number to convert spoken numbers

calendar, datetime for parsing dates

✨ Future Ideas
GUI interface with Tkinter

Email or notification integration

Multi-user support

# 📝 Usage Guide

### 🎤 Commands

- "Add a reminder"
- "Show my reminders"
- "Remove a reminder"
- "Exit"

### 📅 Example Input

**Date:** "August 11"  
**Time:** "3 30 PM" or "Three thirty PM"  
**Repeat Options:** Daily, Weekly, Monthly, Yearly, Once

### 🛑 Notes

- Avoid very long pauses while speaking
- Ensure your mic is configured properly
