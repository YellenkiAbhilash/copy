import os
import json
from flask import Flask, request, render_template, send_file
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

load_dotenv()
app = Flask(__name__)

# Load Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        to_number = request.form['phone']
        call = client.calls.create(
            url='https://copy-3ho4.onrender.com/voice?q=0',
            to=to_number,
            from_=TWILIO_PHONE_NUMBER
        )
        return f"✅ Call initiated! Call SID: {call.sid}"
    return render_template('index.html')

@app.route('/voice', methods=['GET', 'POST'])
def voice():
    q = int(request.args.get("q", 0))

    with open("questions.json") as f:
        questions = json.load(f)

    response = VoiceResponse()

    # ✅ Save the previous answer's recording URL
    if request.method == "POST":
        recording_url = request.values.get("RecordingUrl")
        if recording_url and q > 0:
            with open("responses.txt", "a") as f:
                f.write(f"Q{q}: {questions[q-1]}\nRecording URL: {recording_url}.mp3\n\n")

    # ✅ Ask the next question and record the answer
    if q < len(questions):
        response.say(questions[q])
        response.record(
            action=f"/voice?q={q+1}",
            method="POST",
            maxLength=30,
            playBeep=True,
            timeout=3
        )
    else:
        response.say("Thank you. We have recorded your responses. Goodbye!")
        response.hangup()

    return str(response)

@app.route('/download')
def download_file():
    file_path = "responses.txt"
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return "❌ responses.txt not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
