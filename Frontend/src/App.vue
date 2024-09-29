<script setup>

import Footer from './components/Footer.vue'

</script>

<template>
  <div>
    <router-view></router-view>
    <img src="./assets/background.jpg" class="bottom-image">
    <Footer></Footer>
  </div>
</template>

<style scoped>
.bottom-image {
  position: fixed;
  bottom: -75px;
  left: 150px;
  width: 75%; /* Ensures the image spans the entire width */
  z-index: -1; /* Ensures the image stays behind the content */
}

</style>