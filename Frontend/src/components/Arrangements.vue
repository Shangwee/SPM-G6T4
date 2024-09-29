<script setup>
import NavBar from "./NavBar.vue";
// import Weather from "./Weather.vue";
// import Flight from "./Flight.vue";
</script>

<template>
  <div class="d-flex justify-content-center align-items-center vh-100">
    <NavBar></NavBar>
    <div class="container">
      <h3 class="text-center">Arrangements</h3>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px; /* Adjust the maximum width as needed */
  max-height: 700px;
  overflow-y: auto;
  margin-top: 100px;
  
}

.nav-link {
  padding: 0.5rem 1rem; /* Adjust padding to make tabs more compact */
}

.tab-content {
  margin-top: 1rem; /* Add margin between tabs and content */
  
  
}

</style>
