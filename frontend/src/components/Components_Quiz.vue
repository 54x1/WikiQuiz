<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">Wikipedia Trivia Quiz</h1>
    <div v-if="!showResult">
      <div v-if="currentQuestion">
        <Question :question="currentQuestion" @answered="handleAnswer" />
      </div>
      <div v-else>
        <button class="btn btn-primary" @click="loadFirstQuestion">Start Quiz</button>
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
      currentQuestion: null,
      currentQuestionIndex: 0,
      score: 0,
      totalQuestions: 2, // Set this to the number of questions you have
      showResult: false
    };
  },
  components: {
    Question,
    Result
  },
  methods: {
    async fetchQuestion(index) {
      try {
        const response = await fetch(`http://localhost:5000/get-question?index=${index}`);
        if (response.ok) {
          const question = await response.json();
          this.currentQuestion = question;
        } else {
          this.showResult = true;
        }
      } catch (error) {
        console.error('Error fetching question:', error);
      }
    },
    async handleAnswer(selectedOption) {
      try {
        const response = await fetch('http://localhost:5000/check-answer', {
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
        if (result.correct) {
          this.score++;
        }

        if (this.currentQuestionIndex < this.totalQuestions - 1) {
          this.currentQuestionIndex++;
          this.fetchQuestion(this.currentQuestionIndex);
        } else {
          this.showResult = true;
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
    },
    loadFirstQuestion() {
      this.fetchQuestion(this.currentQuestionIndex);
    }
  }
};
</script>
