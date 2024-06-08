<template>
  <div class="container xs:w-full md:w-1/2 mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">WikiQuiz</h1>
    <div v-if="!showResult">
      <div v-if="currentQuestion">
        <Question 
          :question="currentQuestion" 
          @answered="handleAnswer" 
          :correctAnswer="correctAnswer" 
          :showNextButton="showNextButton" 
          :feedback="feedback"
          @next-question="nextQuestion"
        />
        <transition name="fade">
          <div v-if="feedback" class="mt-4 text-lg" :class="{'text-green-500': feedback.correct, 'text-red-500': !feedback.correct}">
            {{ feedback.message }}
          </div>
        </transition>
      </div>
      <div v-else>
        <div class="mb-4">
          <label for="topic" class="block text-teal-500 font-bold mb-2">Enter a Topic Below</label>
          <input
            type="text"
            v-model="topic"
            id="topic"
            class="input input-bordered w-full mb-4"
            placeholder="e.g. AI, Space, Technology"
          />
          <button class="btn btn-primary" @click="loadFirstQuestion" :disabled="loading">

            
            <span v-if="loading">Loading...</span>
            <span v-else>Start Quiz</span>
          </button>
        </div>
        <h2 v-if="qrCodeUrl" class="font-bold pt-4 text-inherit">Scan Me!</h2>
        <div class="flex justify-center h-80 w-full" v-if="qrCodeUrl">
          <img w-full h-full :src="qrCodeUrl" alt="QR Code" />
        </div>
      </div>
    </div>
    <div v-else>
      <Result :score="score" :total="totalQuestions" @restart="restartQuiz" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Question from './Components_Question.vue';
import Result from './Components_Result.vue';
import { Buffer } from 'buffer';

export default {
  data() {
    return {
      topic: '',
      loading: false,
      currentQuestion: null,
      currentQuestionIndex: 0,
      score: 0,
      totalQuestions: 0,
      showResult: false,
      triviaQuestions: [],
      feedback: null,
      fadeOut: false,
      showNextButton: false,
      correctAnswer: '',
      url: 'https://f750ca24-c3c9-41d9-85e2-4eaaf20945b2-00-207ptbisdfnnt.sisko.replit.dev',
      qrCodeUrl: '',
    };
  },
  components: {
    Question,
    Result
  },
  methods: {
    async generateTrivia() {
      this.loading = true;
      try {
        console.log('Generating trivia for topic:', this.topic);
        const response = await fetch(`${this.url}:5000/generate-trivia`, {
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
            const triviaQuestions = data.trivia_questions;
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
      } finally {
        this.loading = false;
      }
    },
    async loadFirstQuestion() {
      this.currentQuestionIndex = 0;
      this.score = 0;
      this.showResult = false;
      this.triviaQuestions = [];
      this.feedback = null;
      this.fadeOut = false;
      this.showNextButton = false;
      console.log('Loading first question...'); // Log the load start
      await this.generateTrivia(); // Generate the first trivia question
      console.log('First question loaded:', this.currentQuestion); // Log the first question
    },
    async handleAnswer(selectedOption) {
      try {
        console.log('Selected option:', selectedOption); // Log selected option
        const response = await fetch(`${this.url}:5000/check-answer`, {
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
        this.correctAnswer = this.currentQuestion.answer;

        if (result.correct) {
          this.score++;
          feedbackMessage = "Correct! Well done.";
          this.showNextButton = false;
          // Proceed to the next question after showing feedback
          setTimeout(() => {
            this.nextQuestion();
          }, 1000); // Delay before moving to the next question
        } else {
          feedbackMessage = `Incorrect. The correct answer is ${result.correct_answer}.`;
          this.showNextButton = true;
        }

        this.feedback = {
          correct: result.correct,
          message: feedbackMessage
        };

        console.log('Score after answer:', this.score); // Log the score

        // Start the fadeout animation
        this.fadeOut = true;

        setTimeout(() => {
          this.fadeOut = false;
        }, 1500); // Match the duration of the fadeOut animation
      } catch (error) {
        console.error('Error checking answer:', error);
      }
    },
    nextQuestion() {
      this.feedback = null; // Reset feedback for the next question
      this.showNextButton = false; // Hide the "Next" button
      this.correctAnswer = '';

      if (this.currentQuestionIndex < this.totalQuestions - 1) {
        this.currentQuestionIndex++;
        this.currentQuestion = this.triviaQuestions[this.currentQuestionIndex];
        console.log('Next question set:', this.currentQuestion); // Log the next question
      } else {
        this.showResult = true;
        console.log('Quiz finished. Final score:', this.score); // Log the final score
      }
    },
    restartQuiz() {
      this.currentQuestionIndex = 0;
      this.score = 0;
      this.showResult = false;
      this.currentQuestion = null; // Reset current question to show start button again
      this.feedback = null; // Reset feedback
      this.fadeOut = false; // Reset fadeOut state
      this.showNextButton = false; // Reset next button state
      this.correctAnswer = '';
      console.log('Quiz restarted'); // Log the restart
    },
    async generateQRCode() {
      console.log("key", process.env.VUE_APP_JIGSAW_API_KEY);
      try {
        const response = await axios.post('https://api.jigsawstack.com/v1/generate/qrcode', {
          text: `${this.url}:8080/`,
        }, {
          headers: {
            'x-api-key': process.env.VUE_APP_JIGSAW_API_KEY // Use the environment variable here
          },
          responseType: 'arraybuffer' // Important to receive the binary data
        });

        // Convert the binary data to a base64 string
        const base64 = Buffer.from(response.data, 'binary').toString('base64');
        // Create a data URL for the image
        this.qrCodeUrl = `data:image/png;base64,${base64}`;

      } catch (error) {
        console.error('Error generating QR code:', error);
      }
    }
  },
  mounted() {
    this.generateQRCode();
  }
};
</script>

<style>
.fade-out {
  animation: fadeOut 1s forwards;
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
</style>
