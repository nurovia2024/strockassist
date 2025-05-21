from flask import Flask, render_template_string, request, jsonify
import datetime

app = Flask(__name__)

# Stroke risk scoring logic
def calculate_stroke_risk(data):
    score = 0
    details = []

    if data.get('facial_droop') == 'yes':
        score += 2
        details.append("Facial droop detected (+2)")

    if data.get('arm_weakness') == 'yes':
        score += 2
        details.append("Arm weakness detected (+2)")

    if data.get('speech_difficulty') == 'yes':
        score += 2
        details.append("Speech difficulty detected (+2)")

    try:
        onset = int(data.get('onset_time', 0))
        if onset > 3:
            score += 1
            details.append("Symptom onset > 3 hrs (+1)")
    except:
        pass

    age = int(data.get('age', 0))
    if age > 60:
        score += 1
        details.append("Age > 60 (+1)")

    if data.get('history') == 'yes':
        score += 1
        details.append("History of stroke or TIA (+1)")

    if score <= 2:
        risk = "Low"
    elif score <= 4:
        risk = "Moderate"
    else:
        risk = "High"

    return {"risk": risk, "score": score, "details": details}

@app.route("/")
def index():
    return render_template_string(page_template)

@app.route("/assess", methods=["POST"])
def assess():
    data = request.json
    result = calculate_stroke_risk(data)
    return jsonify(result)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    # Dummy logic, in production use LLM or rule-based expansion
    if "what is stroke" in user_input.lower():
        reply = "Stroke is a medical emergency where blood flow to the brain is interrupted."
    elif "signs" in user_input.lower():
        reply = "Common signs include facial drooping, arm weakness, and speech difficulties."
    else:
        reply = "I am your stroke assistant. Ask me anything related to stroke or your symptoms."
    return jsonify({"reply": reply})

page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nurovia Stroke Risk Triage</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f6fb; margin: 0; padding: 0; }
        .container { display: flex; flex-wrap: wrap; padding: 2rem; }
        .form-section, .chat-section { flex: 1; min-width: 300px; padding: 1rem; }
        .card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        h2 { color: #293241; }
        label { display: block; margin-top: 10px; font-weight: 500; }
        input, select { padding: 0.5rem; width: 100%; border-radius: 8px; border: 1px solid #ccc; margin-top: 5px; }
        button { background: #3f72af; color: white; padding: 0.75rem; border: none; border-radius: 8px; margin-top: 1rem; cursor: pointer; width: 100%; }
        .result { background: #e7f5ff; border-left: 4px solid #00b4d8; padding: 1rem; margin-top: 1rem; border-radius: 8px; }
        .chat-box { max-height: 400px; overflow-y: auto; background: #fff; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
        .chat-message { margin: 0.5rem 0; }
        .chat-message.user { text-align: right; }
        .chat-message.bot { text-align: left; color: #444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-section">
            <div class="card">
                <h2>Stroke Risk Screening</h2>
                <label>Facial Droop:</label>
                <select id="facial_droop">
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                </select>

                <label>Arm Weakness:</label>
                <select id="arm_weakness">
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                </select>

                <label>Speech Difficulty:</label>
                <select id="speech_difficulty">
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                </select>

                <label>Onset Time (hours ago):</label>
                <input type="number" id="onset_time" value="1">

                <label>Age:</label>
                <input type="number" id="age" value="45">

                <label>Previous Stroke/TIA History:</label>
                <select id="history">
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                </select>

                <button onclick="submitForm()">Assess Risk</button>
                <div id="result" class="result" style="display:none"></div>
            </div>
        </div>

        <div class="chat-section">
            <div class="card">
                <h2>Stroke Assistant</h2>
                <div class="chat-box" id="chatBox"></div>
                <input type="text" id="chatInput" placeholder="Ask a question...">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        function submitForm() {
            const data = {
                facial_droop: document.getElementById('facial_droop').value,
                arm_weakness: document.getElementById('arm_weakness').value,
                speech_difficulty: document.getElementById('speech_difficulty').value,
                onset_time: document.getElementById('onset_time').value,
                age: document.getElementById('age').value,
                history: document.getElementById('history').value
            };
            fetch('/assess', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(res => res.json()).then(res => {
                let output = `<strong>Risk Level:</strong> ${res.risk}<br/><strong>Score:</strong> ${res.score}<br/>`;
                res.details.forEach(d => { output += `- ${d}<br/>`; });
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').innerHTML = output;
            });
        }

        function sendMessage() {
            const msg = document.getElementById('chatInput').value;
            if (!msg) return;
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML += `<div class='chat-message user'>${msg}</div>`;
            document.getElementById('chatInput').value = "";

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            }).then(res => res.json()).then(res => {
                chatBox.innerHTML += `<div class='chat-message bot'><em>Assistant:</em> ${res.reply}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            });
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860)
