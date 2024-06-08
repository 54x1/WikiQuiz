<template>
  <div class="card shadow-lg p-4 text-center">
      <h2 class="text-2xl font-semibold mb-4">{{ translatedText.quizCompleted }}</h2>
      <p class="mb-4">{{ translatedText.yourScore }} {{ score }} / {{ total }}</p>
      <button class="btn btn-primary" @click="$emit('restart')">{{ translatedText.restartQuiz }}</button>
  </div>
</template>

<script>
export default {
  props: {
    score: Number,
    total: Number,
    translatedText: Object
  },
  methods: {
    restart() {
      this.$emit('restart');
    }
  }
};
</script>
