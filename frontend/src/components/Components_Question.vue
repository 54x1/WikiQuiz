<template>
  <div class="card shadow-lg p-4">
    <h2 class="text-xl font-semibold mb-4">{{ question.question }}</h2>
    <div v-for="option in question.options" :key="option">
      <button class="btn btn-outline w-full mb-2" @click="$emit('answered', option)">
        {{ option }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    question: Object
  }
};
</script>
