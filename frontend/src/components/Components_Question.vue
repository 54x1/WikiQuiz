<template>
   <div class="card shadow-lg p-4">
     <h2 class="text-xl font-semibold mb-4">{{ question.question }}</h2>
     <div v-for="option in question.options" :key="option">
       <button 
         class="btn w-full mb-2" 
         @click="selectAnswer(option)"
         :class="{
           'hover:bg-green-400 bg-green-500 text-white': option === correctAnswer && feedback,
           'opacity-50 hover:bg-red-300 bg-red-500 text-white': option === selectedOption && option !== correctAnswer && feedback,
           'opacity-50 cursor-not-allowed': feedback !== null && option !== correctAnswer && option !== selectedOption,
           'btn-outline': feedback === null || (feedback !== null && option !== correctAnswer && option !== selectedOption)
         }">
         {{ option }}
       </button>
     </div>
     <button v-if="showNextButton" class="btn btn-primary mt-4" @click="nextQuestion">Next</button>
   </div>
 </template>

 <script>
 export default {
   props: {
     question: Object,
     correctAnswer: String,
     showNextButton: Boolean,
     feedback: Object
   },
   data() {
     return {
       selectedOption: null,
     };
   },
   methods: {
     selectAnswer(option) {
       if (!this.feedback) {
         this.selectedOption = option;
         this.$emit('answered', option);
       }
     },
     nextQuestion() {
       this.$emit('next-question');
     }
   },
   watch: {
     question() {
       this.selectedOption = null; // Reset selected option when question changes
     }
   }
 };
 </script>