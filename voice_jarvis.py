import openai
import speech_recognition as sr
import pyttsx3

# Set your OpenAI API key here
openai.api_key = 'YOUR_OPENAI_API_KEY'

engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # female voice

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio, language='en-in')
        print("You said:", query)
    except Exception:
        speak("Sorry, I did not get that. Please say it again.")
        return ""
    return query

def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Rudra's helpful AI assistant."},
            {"role": "user", "content": question}
        ],
        max_tokens=150,
        temperature=0.7
    )
    answer = response['choices'][0]['message']['content']
    return answer

def main():
    speak("Hello Rudra, I am your voice assistant. How can I help you today?")
    while True:
        query = listen()
        if query.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye Rudra! Have a great day.")
            break
        if query:
            answer = ask_openai(query)
            speak(answer)

if __name__ == "__main__":
    main()
