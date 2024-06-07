<template>
  <div class="card shadow-lg p-4 text-center">
    <h2 class="text-2xl font-semibold mb-4">Quiz Completed!</h2>
    <p class="mb-4">Your Score: {{ score }} / {{ total }}</p>
    <button class="btn btn-primary" @click="$emit('restart')">Restart Quiz</button>
  </div>
</template>

<script>
export default {
  props: {
    score: Number,
    total: Number
  }
};
</script>
