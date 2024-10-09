<template> 
  <div>
    <div class="container mt-3 pt-5">
      <div class="d-flex justify-content-center mb-4">
        <button @click="filterRequests('All')" class="btn btn-outline-primary mx-2">All</button>
        <button @click="filterRequests('Pending')" class="btn btn-outline-warning mx-2">Pending</button>
        <button @click="filterRequests('Approved')" class="btn btn-outline-success mx-2">Approved</button>
        <button @click="filterRequests('Rejected')" class="btn btn-outline-danger mx-2">Rejected</button>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead class="thead-dark">
            <tr>
              <th>Request ID</th>
              <th>Employee ID</th>
              <th>Employee Name</th> <!-- Updated Header -->
              <th>Request Date</th>
              <th>Reason</th>
              <th>Status</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in filteredRequests" :key="request.Request_ID">
              <td>{{ request.Request_ID }}</td>
              <td>{{ request.Employee_ID }}</td>
              <td>{{ request.employeeName }}</td> <!-- Display User Name -->
              <td>{{ request.Date }}</td>
              <td>{{ request.Reason }}</td>
              <td>
                <span :class="statusBadgeClass(request.Status)">{{ request.Status }}</span>
              </td>
              <td class="text-center">
                <button v-if="request.Status === 'Pending'" @click="updateStatus(request.Request_ID, 'Approved')" class="btn btn-success btn-sm mx-1">Approve</button>
                <button v-if="request.Status === 'Pending'" @click="updateStatus(request.Request_ID, 'Rejected')" class="btn btn-danger btn-sm mx-1">Reject</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const requests = ref([]);
const enrichedRequests = ref([]); // New variable for enriched requests
const filteredRequests = ref([]);

// Get Staff ID from session storage
const staffId = sessionStorage.getItem('staffID');

// Fetch requests for the approver
const fetchRequests = async () => {
  try {
    const response = await axios.get(`http://localhost:5003/request/approver/${staffId}`);
    requests.value = response.data;
    enrichedRequests.value = await enrichRequestsWithUserDetails(requests.value); // Enrich requests with user details
    filterRequests('All'); // Set initial filter to show all requests
  } catch (error) {
    console.error('Error fetching requests:', error);
  }
};

// Fetch user details for each request
const enrichRequestsWithUserDetails = async (requests) => {
  const enrichedRequests = await Promise.all(requests.map(async (request) => {
    try {
      const userResponse = await axios.get(`http://localhost:5001/user/${request.Employee_ID}`);
      const user = userResponse.data;
      return {
        ...request,
        employeeName: `${user.Staff_FName} ${user.Staff_LName}`, // Combine first and last name
        position: user.Position,
        team: user.Dept,
      };
    } catch (error) {
      console.error('Error fetching user details for request:', request.Request_ID, error);
      return {
        ...request,
        employeeName: 'Unknown', // Fallback in case of error
      };
    }
  }));
  return enrichedRequests;
};

onMounted(() => {
  fetchRequests();
});

// Filter requests based on status
const filterRequests = (status) => {
  if (status === 'All') {
    filteredRequests.value = enrichedRequests.value; // Use enriched requests for filtering
  } else {
    filteredRequests.value = enrichedRequests.value.filter(request => request.Status === status);
  }
};

const statusBadgeClass = (status) => {
  if (status === 'Pending') return 'badge bg-warning text-dark';
  if (status === 'Approved') return 'badge bg-success';
  if (status === 'Rejected') return 'badge bg-danger';
};

const updateStatus = async (requestId, newStatus) => {
  try {
    await axios.put(`http://localhost:5003/request/update/${requestId}`, { Status: newStatus });
    // Refresh the requests after updating
    await fetchRequests();
  } catch (error) {
    console.error('Error updating status:', error);
  }
};
</script>

<style>
/* Adjust margin-top for the container to avoid affecting navbar */
.container {
  margin-top: 0px; /* Adjust this value as needed */
}

.thead-dark {
  background-color: #343a40;
  color: white;
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

.badge {
  font-size: 0.9em;
  padding: 0.5em;
}

.btn {
  min-width: 100px;
}
</style>
