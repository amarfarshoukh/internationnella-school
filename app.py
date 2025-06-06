
from flask import Flask, request, jsonify, Response,json
from flask_cors import CORS
from student_pipeline import analyze_student
import requests  # For making requests to Ollama's API

app = Flask(__name__)
CORS(app)

# Ollama configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API endpoint
PHI3_MODEL_NAME = "phi3:mini"  # The model name you used with 'ollama pull phi3'

CSV_PATH = r"C:\Users\user\OneDrive - Lebanese University\Desktop\student_dataset_with_exam_date.csv"
NEWSAPI_KEY = "9681360b2f5f452cb6ea040341e58943"

def query_phi3(prompt):
    """Send a prompt to the locally running Phi-3 model via Ollama"""
    payload = {
        "model": PHI3_MODEL_NAME,
        "prompt": prompt,
        "stream": False  # We want a single response
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"Error querying Phi-3 model: {str(e)}")
        return None

@app.route('/student_analysis', methods=['POST', 'OPTIONS'])
def get_student_analysis():
    print("\n=== New Request ===")
    print("Method:", request.method)
    
    if request.method == 'OPTIONS':
        print("Handling OPTIONS preflight")
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    print("Received POST with data:", request.json)
    
    try:
        cntstuid = request.json.get('cntstuid')
        print("Processing student ID:", cntstuid)
        
        analysis = analyze_student(CSV_PATH, cntstuid, NEWSAPI_KEY)
        print("Generated analysis:", analysis[:100] + "...")  # Print first 100 chars
        
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot_stream', methods=['POST'])
def chatbot_stream():
    data = request.get_json()  # Read data BEFORE entering the generator

    def generate(user_input):
        prompt = f"<|user|>\n{user_input}\n<|assistant|>"
        payload = {"model": PHI3_MODEL_NAME, "prompt": prompt, "stream": True}
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    chunk = line.decode('utf-8')
                    try:
                        reply = json.loads(chunk).get("response", "")
                        if reply:
                            yield reply
                    except Exception:
                        continue

    user_input = data.get("message", "").strip()
    return Response(generate(user_input), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)