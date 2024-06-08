from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from groq import Groq
from dotenv import load_dotenv
import wikipediaapi

app = Flask(__name__)
CORS(app)
# Load environment variables from .env file
load_dotenv()
trivia_questions = []

# search_query = "Machine learning"  # Change to use input


def get_wikipedia_page(search_query):
  wiki = wikipediaapi.Wikipedia(
      'WikiQuiz (Wiki@Quiz.com)',
      'en')  # Replace 'en' with your language code if needed

  # Change to dynamic input later.
  page_py = wiki.page(search_query)

  if page_py.exists():
    #print(f'Title: {page_py.title}')
    #print(f'Summary: {page_py.summary}')
    print(f'Summary: {page_py.text}')
    #print(f'Full Url: {page_py.fullurl}')
    return page_py.summary

  else:  # Get the user to input a different their entry.
    return print(f'No page found for {search_query}')


# Create the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt Template
system_prompt = {
    "role":
    "system",
    "content":
    """Given the following prompt, create 4 multiple choice quizzes in JSON format.
Each question should have 4 different options, and only one of them should be correct.
The options should be unambiguous.
The question should also briefly mention the general topic of the text so that it can be understood in isolation.
Each question should not give hints to answer the other questions.
Include challenging questions, which require reasoning.
respond with JSON only, no markdown or descriptions, ensure all options are separated and display the correct answer as the correct option.
example JSON format you should absolutely follow:
  [
    {
      "question": "text of the question",
      "options": ["option", "option", "option", "option"],
      "answer": "correct option"
    }, ... # continue for all questions
  ]"""
}


@app.route('/', methods=['GET'])
def backend_loded():
  return jsonify({"message": "WikiQuiz API"})


# @app.route('/get-question', methods=['GET'])
# def get_question():
#   try:
#     index = int(request.args.get('index', 0))
#     if index < len(trivia_questions):
#       question = trivia_questions[index]
#       return jsonify(question)
#     else:
#       return jsonify({"message": "No more questions"}), 404
#   except ValueError:
#     return jsonify({"message": "Invalid question index"}), 400


@app.route('/generate-trivia', methods=['POST'])
def generate_trivia():
  global trivia_questions
  try:
    topic = request.json.get('topic')
    user_content = get_wikipedia_page(topic)
    if not user_content:
      return jsonify({"message": "No page found for the given topic"}), 404

    chat_history = [
        system_prompt, {
            "role": "user",
            "content": user_content,
        }
    ]

    chat_completion = client.chat.completions.create(
        messages=chat_history,
        max_tokens=800,
        model="llama3-8b-8192",
        temperature=1.1,
        stream=False,
    )

    trivia_questions_json = chat_completion.choices[0].message.content
    print("trivia_questions", trivia_questions)
    try:
      trivia_questions = json.loads(trivia_questions_json)
      if isinstance(trivia_questions, list):
        print("Generated trivia questions:", trivia_questions)
        return jsonify({"trivia_questions": trivia_questions})
      else:
        raise ValueError("Invalid format for trivia questions")
    except json.JSONDecodeError as e:
      print(f"JSON decode error: {e}")
      return jsonify({"error": "Failed to parse trivia questions"}), 500

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/check-answer', methods=['POST'])
def check_answer():
  global trivia_questions
  try:
    data = request.json
    index = int(data.get('index'))
    user_answer = data.get('answer')
    print(f"Received index: {index}, user_answer: {user_answer}")

    if isinstance(trivia_questions,
                  list) and 0 <= index < len(trivia_questions):
      correct_answer = trivia_questions[index]['answer']
      is_correct = user_answer == correct_answer
      print(f"Correct answer: {correct_answer}, Is correct: {is_correct}")
      return jsonify({"correct": is_correct, "correct_answer": correct_answer})
    else:
      print(
          f"Invalid question index or trivia_questions is not a list. trivia_questions: {trivia_questions}"
      )
      return jsonify({"message": "Invalid question index"}), 400
  except (ValueError, TypeError) as e:
    print(f"Error in check_answer: {e}")
    return jsonify({"message": "Invalid data"}), 400


if __name__ == '__main__':
  app.run(debug=True)
