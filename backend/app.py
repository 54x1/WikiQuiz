from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app) 
# Load environment variables from .env file
load_dotenv()

# Create the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Set the system prompt for the trivia theme
system_prompt = {
    "role": "system",
    "content": "You are a trivia quiz assistant. You generate trivia questions based on Wikipedia articles."
}

# Sample questions
trivia_questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "Berlin", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "Who wrote '1984'?",
        "options": ["George Orwell", "Aldous Huxley", "Ray Bradbury"],
        "answer": "George Orwell"
    },
    # Add more questions here or generate dynamically
]

@app.route('/get-question', methods=['GET'])
def get_question():
    try:
        index = int(request.args.get('index', 0))
        if index < len(trivia_questions):
            question = trivia_questions[index]
            return jsonify(question)
        else:
            return jsonify({"message": "No more questions"}), 404
    except ValueError:
        return jsonify({"message": "Invalid question index"}), 400

@app.route('/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    index = data.get('index')
    user_answer = data.get('answer')

    if index < len(trivia_questions):
        correct_answer = trivia_questions[index]['answer']
        is_correct = user_answer == correct_answer
        return jsonify({"correct": is_correct, "correct_answer": correct_answer})
    else:
        return jsonify({"message": "Invalid question index"}), 400

@app.route('/generate-trivia', methods=['POST'])
def generate_trivia():
    topic = request.json.get('topic')
    chat_history = [system_prompt, {"role": "user", "content": f"Generate a trivia question about {topic}."}]

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=chat_history,
        max_tokens=100,
        temperature=1.2
    )

    trivia_question = response.choices[0].message.content
    return jsonify({"trivia_question": trivia_question})

if __name__ == '__main__':
    app.run(debug=True)
