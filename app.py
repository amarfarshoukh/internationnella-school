
from flask import Flask, request, jsonify
from flask_cors import CORS
from student_pipeline import analyze_student

app = Flask(__name__)
CORS(app)

CSV_PATH = r"C:\Users\user\OneDrive - Lebanese University\Desktop\student_dataset_with_exam_date.csv" ## HON MN EL DESKTOP UPDATE IF NEED ELSEWHERE!
NEWSAPI_KEY = "9681360b2f5f452cb6ea040341e58943"


@app.route('/student_analysis', methods=['POST', 'OPTIONS'])
def get_student_analysis():
    print("\n=== New Request ===")
    print("Method:", request.method)
    
    if request.method == 'OPTIONS':
        print("Handling OPTIONS preflight")
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    print("Received POST with data:", request.json)
    
    try:
        cntstuid = request.json.get('cntstuid')
        print("Processing student ID:", cntstuid)
        
        analysis = analyze_student(CSV_PATH, cntstuid, NEWSAPI_KEY, HF_TOKEN)
        print("Generated analysis:", analysis[:100] + "...")  # Print first 100 chars
        
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500


#
PREDEFINED_RESPONSES = {
    "hi": "Hello! I'm your friendly AI assistant. Ask me anything fun or school-related!",
    "hello": "Hey there! I'm ready to chat about learning, stories, or just have some fun!",
    "tell me a story": "Once, a curious student built a robot that helped with homework. The robot became so smart, it started asking its own questions!",
    "tell me a joke": "Why did the math book look sad? Because it had too many problems!",
    "write a poem": "In science labs with lights so bright,\nIdeas spark and futures light.",
    "motivate me": "You're capable of amazing things. Every great mind started with a question — keep asking!",
    "what is photosynthesis": "Photosynthesis is how plants turn sunlight, carbon dioxide, and water into food. It’s their way of making lunch!",
    "who discovered gravity": "Gravity was famously described by Sir Isaac Newton — yes, the apple guy!",
    "explain the water cycle": "The water cycle has evaporation, condensation, precipitation, and collection. It keeps water moving around Earth!",
    "how do i stay focused": "Try the 25-minute focus technique: study for 25, rest for 5. It helps your brain recharge!",
    "what is pi": "Pi is a special number in math (about 3.14159) that helps us measure circles!",
    "what is the capital of france": "The capital of France is Paris — known for its Eiffel Tower and amazing art.",
    "who is albert einstein": "Albert Einstein was a brilliant physicist who developed the theory of relativity.",
    "what is an atom": "An atom is the smallest building block of matter — everything you see is made of atoms!",
    "why is the sky blue": "The sky looks blue because sunlight gets scattered by Earth's atmosphere — blue light scatters more!"
}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_input = data.get("message", "").strip().lower()

    if not user_input:
        return jsonify({"reply": "Please enter a message."})

    response = PREDEFINED_RESPONSES.get(user_input)

    if response:
        return jsonify({"reply": response})
    else:
        return jsonify({
            "reply": "I'm just a simple demo bot! Try asking something like 'What is photosynthesis?' or 'Tell me a story'."
        })

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



    
