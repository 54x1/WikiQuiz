<template>
  <div class="container xs:w-full md:w-1/2 mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">{{ this.title }}</h1>
    <div v-if="!quizStarted" class="mb-4">
      <label for="language" class="block text-teal-500 font-bold mb-2">{{ translatedText.selectLanguage }}</label>
      <div class="flex justify-center space-x-4">
        <button class="btn btn-secondary" @click="selectLanguage('en')">English</button>
        <button class="btn btn-secondary" @click="selectLanguage('zh')">Mandarin Chinese</button>
        <button class="btn btn-secondary" @click="selectLanguage('es')">Spanish</button>
        <button class="btn btn-secondary" @click="selectLanguage('hi')">Hindi</button>
      </div>
    </div>
    <div v-if="selectedLanguage">
      <div v-if="!showResult">
        <div v-if="currentQuestion">
          <Question 
            :question="currentQuestion" 
            @answered="handleAnswer" 
            :correctAnswer="correctAnswer" 
            :showNextButton="showNextButton" 
            :feedback="feedback"
            @next-question="nextQuestion"
            :nextButtonText="translatedText.nextButton"
          />
          <transition name="fade">
            <div v-if="feedback" class="mt-4 text-lg" :class="{'text-green-500': feedback.correct, 'text-red-500': !feedback.correct}">
              {{ feedback.message }}
            </div>
          </transition>
        </div>
        <div v-else>
          <div class="mb-4">
            <label for="topic" class="block text-teal-500 font-bold mb-2">{{ translatedText.enterTopic }}</label>
            <input
              type="text"
              v-model="topic"
              id="topic"
              class="input input-bordered w-full mb-4"
              :placeholder="translatedText.topicPlaceholder"
            />
            <button class="btn btn-primary" @click="loadFirstQuestion" :disabled="loading">
              <span v-if="loading">{{ translatedText.loading }}</span>
              <span v-else>{{ translatedText.startQuiz }}</span>
            </button>
          </div>
        </div>
      </div>
      <div v-else>
        <Result :score="score" :total="totalQuestions" @restart="restartQuiz" :translatedText="translatedText" />
      </div>
    </div>
    <div v-if="!quizStarted"> 
      <h2 v-if="qrCodeUrl" class="font-bold pt-4 text-inherit">{{ translatedText.scanMe }}</h2>
      <div class="flex justify-center h-80 w-full" v-if="qrCodeUrl">
        <img w-full h-full :src="qrCodeUrl" alt="QR Code" />
      </div>
    </div>
  </div>
</template>



<script>
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
      selectedLanguage: '',
      quizStarted: false,
      url: 'https://f750ca24-c3c9-41d9-85e2-4eaaf20945b2-00-207ptbisdfnnt.sisko.replit.dev',
      qrCodeUrl: '',
      title: 'WikiKwiz',
      defaultText: {
        selectLanguage: 'Select Language',
        enterTopic: 'Enter a Topic Below',
        topicPlaceholder: 'e.g. AI, Space, Technology',
        loading: 'Loading...',
        startQuiz: 'Start Quiz',
        scanMe: 'Scan Me!',
        correctMessage: 'Correct! Well done.',
        incorrectMessage: 'Incorrect. The correct answer is',
        nextButton: 'Next',
        quizCompleted: 'Quiz Completed!',
        yourScore: 'Your Score:',
        restartQuiz: 'Restart Quiz'
      },
      translatedText: {
        selectLanguage: 'Select Language',
        enterTopic: 'Enter a Topic Below',
        topicPlaceholder: 'e.g. AI, Space, Technology',
        loading: 'Loading...',
        startQuiz: 'Start Quiz',
        scanMe: 'Scan Me!',
        correctMessage: 'Correct! Well done.',
        incorrectMessage: 'Incorrect. The correct answer is',
        nextButton: 'Next',
        quizCompleted: 'Quiz Completed!',
        yourScore: 'Your Score:',
        restartQuiz: 'Restart Quiz'
      },
    };
  },
  components: {
    Question,
    Result
  },
  methods: {
    selectLanguage(language) {
      this.selectedLanguage = language;
      console.log('Language selected:', this.selectedLanguage); // Log selected language
      if (language === 'en') {
        this.translatedText = { ...this.defaultText };
      } else {
        this.translatePage(); // Translate static text on the page
      }
    },
    async translatePage() {
      const endpoint = "https://api.jigsawstack.com/v1/ai/translate";
      const apiKey = process.env.VUE_APP_JIGSAW_API_KEY; // Use your actual API key

      try {
        const textsToTranslate = Object.values(this.defaultText);
        const translatedValues = await Promise.all(textsToTranslate.map(async (text) => {
          const options = {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-api-key": apiKey
            },
            body: JSON.stringify({
              current_language: "en",
              target_language: this.selectedLanguage,
              text
            }),
          };

          const result = await fetch(endpoint, options);
          const data = await result.json();

          if (data && data.translated_text) {
            return data.translated_text;
          } else {
            console.error('Translation failed for text:', text);
            return text; // fallback to the original text if translation fails
          }
        }));

        const keys = Object.keys(this.defaultText);
        keys.forEach((key, index) => {
          this.translatedText[key] = translatedValues[index];
        });

        console.log('Page text translated:', this.translatedText); // Log translated page text
      } catch (error) {
        console.error('Error translating page text:', error);
      }
    },
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
            this.triviaQuestions = data.trivia_questions;
            await this.translateQuestions(); // Translate the questions after generating them
            this.totalQuestions = this.triviaQuestions.length;
            this.currentQuestion = this.triviaQuestions[this.currentQuestionIndex];
            console.log('Current question set:', this.currentQuestion); // Log the current question
            this.quizStarted = true; // Quiz has started
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
          feedbackMessage = this.translatedText.correctMessage;
          this.showNextButton = false;
          // Proceed to the next question after showing feedback
          setTimeout(() => {
            this.nextQuestion();
          }, 1000); // Delay before moving to the next question
        } else {
          feedbackMessage = `${this.translatedText.incorrectMessage} ${result.correct_answer}.`;
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
      this.quizStarted = false; // Reset quiz started state
      this.translatedText = { ...this.defaultText }; // Reset to default text
      console.log('Quiz restarted'); // Log the restart
    },
    async generateQRCode() {
      console.log("key", process.env.VUE_APP_JIGSAW_API_KEY);
      try {
        const response = await fetch('https://api.jigsawstack.com/v1/generate/qrcode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': process.env.VUE_APP_JIGSAW_API_KEY // Use the environment variable here
          },
          body: JSON.stringify({
            text: `${this.url}:8080/`,
          })
        });

        if (response.ok) {
          const data = await response.arrayBuffer();
          // Convert the binary data to a base64 string
          const base64 = Buffer.from(data).toString('base64');
          // Create a data URL for the image
          this.qrCodeUrl = `data:image/png;base64,${base64}`;
        } else {
          console.error('Error generating QR code:', response.statusText);
        }
      } catch (error) {
        console.error('Error generating QR code:', error);
      }
    },
    async translateQuestions() {
      if (!this.triviaQuestions.length) {
        return;
      }

      const endpoint = "https://api.jigsawstack.com/v1/ai/translate";
      const apiKey = process.env.VUE_APP_JIGSAW_API_KEY; // Use your actual API key

      try {
        const translatedQuestions = await Promise.all(this.triviaQuestions.map(async (question) => {
          const options = {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-api-key": apiKey
            },
            body: JSON.stringify({
              current_language: "en",
              target_language: this.selectedLanguage,
              text: question.question
            }),
          };

          const result = await fetch(endpoint, options);
          const data = await result.json();

          if (data && data.translated_text) {
            question.question = data.translated_text;
          } else {
            console.error('Translation failed for question:', question);
          }

          const translatedOptions = await Promise.all(question.options.map(async (option) => {
            const optionOptions = {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey
              },
              body: JSON.stringify({
                current_language: "en",
                target_language: this.selectedLanguage,
                text: option
              }),
            };

            const optionResult = await fetch(endpoint, optionOptions);
            const optionData = await optionResult.json();

            if (optionData && optionData.translated_text) {
              return optionData.translated_text;
            } else {
              console.error('Translation failed for option:', option);
              return option; // fallback to the original option if translation fails
            }
          }));

          question.options = translatedOptions;

          const answerOptions = {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-api-key": apiKey
            },
            body: JSON.stringify({
              current_language: "en",
              target_language: this.selectedLanguage,
              text: question.answer
            }),
          };

          const answerResult = await fetch(endpoint, answerOptions);
          const answerData = await answerResult.json();

          if (answerData && answerData.translated_text) {
            question.answer = answerData.translated_text;
          } else {
            console.error('Translation failed for answer:', question.answer);
          }

          return question;
        }));

        this.triviaQuestions = translatedQuestions;
        this.currentQuestion = this.triviaQuestions[this.currentQuestionIndex];
      } catch (error) {
        console.error('Error translating questions:', error);
      }
    }
  },
  mounted() {
    this.generateQRCode();
  }
};
</script>
