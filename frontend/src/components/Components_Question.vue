<template>
  <div class="card shadow-lg p-4">
    <h2 v-if="question && question.question" class="text-xl font-semibold mb-4">{{ question.question }}</h2>
    <div v-if="question && question.options">
      <div v-for="option in question.options" :key="option">
        <button class="btn btn-outline w-full mb-2" @click="$emit('answered', option)">
          {{ option }}
        </button>
      </div>
    </div>
    <div v-else>
      <p>Loading question...</p>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    question: {
      type: Object,
      required: true,
      default: () => ({
        question: '',
        options: []
      })
    }
  },
  watch: {
    question(newVal) {
      console.log('Question prop updated:', newVal);
    }
  },
  mounted() {
    console.log('Question component mounted with:', this.question);
  }
};
</script>

<style scoped>
.card {
  max-width: 600px;
  margin: auto;
}
</style>
