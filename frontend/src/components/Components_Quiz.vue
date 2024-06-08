<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">Wikipedia Trivia Quiz</h1>
    <div v-if="!showResult">
      <div v-if="currentQuestion">
        <Question :question="currentQuestion" @answered="handleAnswer" />
        <div v-if="feedback" class="mt-4 text-lg" :class="{'text-green-500': feedback.correct, 'text-red-500': !feedback.correct}">
          {{ feedback.message }}
        </div>
      </div>
      <div v-else>
        <div class="mb-4">
          <label for="topic" class="block text-gray-700">Enter a Topic:</label>
          <input
            type="text"
            v-model="topic"
            id="topic"
            class="input input-bordered w-full mb-4"
            placeholder="e.g., Space, History, Technology"
          />
          <button class="btn btn-primary" @click="loadFirstQuestion">Start Quiz</button>
        </div>
      </div>
    </div>
    <div v-else>
      <Result :score="score" :total="totalQuestions" @restart="restartQuiz" />
    </div>
  </div>
</template>

<script>
import Question from './Components_Question.vue';
import Result from './Components_Result.vue';

export default {
  data() {
    return {
      topic: '',
      currentQuestion: null,
      currentQuestionIndex: 0,
      score: 0,
      totalQuestions: 0,
      showResult: false,
      triviaQuestions: [],
      feedback: null
    };
  },
  components: {
    Question,
    Result
  },
  methods: {
    async generateTrivia() {
      try {
        console.log('Generating trivia for topic:', this.topic);
        const response = await fetch('https://f750ca24-c3c9-41d9-85e2-4eaaf20945b2-00-207ptbisdfnnt.sisko.replit.dev:5000/generate-trivia', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ topic: this.topic })
        });

        if (response.ok) {
    const data = await response.json();
          console.log('Response from server:', data); // Log the response
          if (data.trivia_questions) {
            const triviaQuestions = data.trivia_questions
            console.log('Parsed trivia questions:', triviaQuestions); // Log the parsed trivia questions
            this.triviaQuestions = triviaQuestions;
            this.totalQuestions = this.triviaQuestions.length;
            this.currentQuestion = this.triviaQuestions[this.currentQuestionIndex];
            console.log('Current question set:', this.currentQuestion); // Log the current question
          } else {
            console.error('Invalid trivia question format');
          }
        } else {
          console.error('Failed to generate trivia question');
        }
      } catch (error) {
        console.error('Error generating trivia question:', error);
      }
    },
    async loadFirstQuestion() {
      this.currentQuestionIndex = 0;
      this.score = 0;
      this.showResult = false;
      this.triviaQuestions = [];
      this.feedback = null;
      console.log('Loading first question...'); // Log the load start
      await this.generateTrivia(); // Generate the first trivia question
      console.log('First question loaded:', this.currentQuestion); // Log the first question
    },
    async handleAnswer(selectedOption) {
      try {
        console.log('Selected option:', selectedOption); // Log selected option
        const response = await fetch('https://f750ca24-c3c9-41d9-85e2-4eaaf20945b2-00-207ptbisdfnnt.sisko.replit.dev:5000/check-answer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            index: this.currentQuestionIndex,
            answer: selectedOption
          })
        });

        const result = await response.json();
        console.log('Check answer result:', result); // Log the result

        let feedbackMessage;
        if (result.correct) {
          this.score++;
          feedbackMessage = "Correct! Well done.";
        } else {
          feedbackMessage = `Incorrect. The correct answer is ${result.correct_answer}.`;
        }

        this.feedback = {
          correct: result.correct,
          message: feedbackMessage
        };

        console.log('Score after answer:', this.score); // Log the score

        if (this.currentQuestionIndex < this.totalQuestions - 1) {
          this.currentQuestionIndex++;
          this.currentQuestion = this.triviaQuestions[this.currentQuestionIndex];
          this.feedback = null; // Reset feedback for the next question
          console.log('Next question set:', this.currentQuestion); // Log the next question
        } else {
          this.showResult = true;
          console.log('Quiz finished. Final score:', this.score); // Log the final score
        }
      } catch (error) {
        console.error('Error checking answer:', error);
      }
    },
    restartQuiz() {
      this.currentQuestionIndex = 0;
      this.score = 0;
      this.showResult = false;
      this.currentQuestion = null; // Reset current question to show start button again
      this.feedback = null; // Reset feedback
      console.log('Quiz restarted'); // Log the restart
    }
  }
};
</script>
