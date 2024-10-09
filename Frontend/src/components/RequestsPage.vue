<script setup>
import NavBar from "./NavBar.vue";
import Requests from "./Requests.vue";
</script>
<template>
  <div>
    <NavBar></NavBar>
    <br>
    <div class="container-fluid">
      <div class="row text-center justify-content-center">
        <div class="col-12">
          <h3 class="mb-3">My Requests</h3> <!-- Remove bottom margin to bring closer to the button -->
        </div>
        <div class="col-12 col-md-8 calendar-wrapper">
          <Requests scheduleType="user"></Requests>
        </div>
      </div>
      <br>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {

    };
  },

  methods: {
    
  },
  components: {
    Requests
  },  
};
</script>

<style scoped>
.calendar-wrapper {
  max-width: 100%; /* Adjust the width here */
  margin: 0 auto;   /* Center the calendar */
  padding: 20px;    /* Add some padding around the calendar */
}

.container-fluid {
  margin-top: 100px;
}
</style>
