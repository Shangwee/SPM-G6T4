<template>
  <nav class="navbar navbar-expand-lg py-3 navbar-white bg-white border rounded-2 border-2 shadow-sm fixed-top">
    <div class="container">
      <router-link to="/" class="navbar-brand">
        <h3 class="text-primary">All-in-One</h3>
      </router-link>

      <button
        type="button"
        class="navbar-toggler"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="navbarSupportedContent" class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item btn nav-link navbar-btn-hover" :class="{ 'navbar-btn-active': activeButton === 'Own Schedule' }" @click="handleOwnSchedule">My Schedule</li>
          <li class="nav-item btn nav-link navbar-btn-hover" :class="{ 'navbar-btn-active': activeButton === 'Team Schedule' }" @click="handleTeamSchedule">Team Schedule</li>
          <li v-if="userRole === 2" class="nav-item btn nav-link navbar-btn-hover" :class="{ 'navbar-btn-active': activeButton === 'Arrangements' }" @click="handleArrangements">Arrangements</li>
          <li v-if="userRole === 3" class="nav-item btn nav-link navbar-btn-hover" :class="{ 'navbar-btn-active': activeButton === 'Requests' }" @click="handleRequests">Requests</li>
          <li class="nav-item btn nav-link navbar-btn-hover" :class="{ 'navbar-btn-active': activeButton === 'Notifications' }" @click="handleNotifications">Notifications</li>
          <li class="nav-item btn ml-3 nav-link navbar-btn" @click="handleLogin">Logout</li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'NavBar',
  setup() {
    const router = useRouter();
    const activeButton = ref(null);
    const userRole = ref(null);
    const staffID = ref(null);
    const loading = ref(true); // Loading state

    // Fetch user role from backend
    const fetchUserRole = async () => {
      try {
        staffID.value = JSON.parse(sessionStorage.getItem('staffID'));
        const response = await fetch(`http://localhost:5001/user/${staffID.value}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const data = await response.json();
        userRole.value = data.Role;
      } catch (error) {
        console.error('Failed to fetch user role:', error);
      } finally {
        loading.value = false; // Set loading to false after fetching
      }
    };

    // Check if user logged in
    const checkLoggedIn = () => {
      if (!staffID.value) {
        router.push('/login');
      }
    };

    const handleLogin = async () => {
      sessionStorage.clear();
      router.push('/login');
    };

    const handleOwnSchedule = () => {
      router.push('/ownschedule');
      activeButton.value = 'Own Schedule';
    };

    const handleTeamSchedule = () => {
      router.push('/teamschedule');
      activeButton.value = 'Team Schedule';
    };

    const handleArrangements = () => {
      router.push('/arrangements');
      activeButton.value = 'Arrangements';
    };

    const handleRequests = () => {
      router.push('/requests');
      activeButton.value = 'Requests';
    };

    const handleNotifications = async () => {
      router.push('/notifications');
      activeButton.value = 'Notifications';
    };

    onMounted(() => {
      fetchUserRole();
      checkLoggedIn();
    });

    return { handleOwnSchedule, handleTeamSchedule, handleArrangements, handleLogin, handleRequests, handleNotifications, activeButton, userRole, loading };
  },
};
</script>

<style scoped>
.nav-link.aria-current {
  background-color: #f5f5f5;
  border-bottom: 2px solid #000;
}
.nav-item {
  margin: 10px;
}

.navbar-btn-hover:hover,
.navbar-btn-active {
  background-color: #ffffff;
  color: rgb(0, 0, 0);
  font-weight: bold;
}
.navbar-btn:hover {
  background-color: #ffffff;
  color: red;
  font-weight: bold;
}

.navbar-nav {
  width: 100%;
  display: flex;
  justify-content: space-between;
}
.navbar-nav .nav-item {
  flex: 1;
  text-align: center;
}
.navbar-brand:hover {
  background-color: transparent; /* Change to the desired background color or none */
}
</style>
