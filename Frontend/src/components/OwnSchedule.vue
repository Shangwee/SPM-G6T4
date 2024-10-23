<script setup>
import { ref, onMounted } from 'vue';
import NavBar from "./NavBar.vue";
import axios from 'axios'; // Import Axios

// Track selected date and form visibility
const selectedDay = ref(null);
const currentDate = ref(new Date());
const hoveredDay = ref(null); // To track the hovered date
const showForm = ref(false); // To track the visibility of the form
const dayToConfirm = ref(null); // Track the day being confirmed for work-from-home
const reason = ref(''); // Track the reason for working from home

const showOptionsPopup = ref(false); // Track visibility of options popup
const showWithdrawConfirmation = ref(false); // Track visibility of withdraw confirmation
const dayToWithdraw = ref(null); // Track the day being withdrawn
const daysInMonth = ref([]);
const wfhDates = ref([]); // Store the dates the user has applied for WFH with their status
const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Function to get the days of the month
const getDaysInMonth = (year, month) => {
  const days = [];
  const firstDay = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();

  // Fill in the empty days before the first day of the month
  for (let i = 0; i < firstDay; i++) {
    days.push('');
  }

  // Fill in the days of the month
  for (let day = 1; day <= lastDate; day++) {
    days.push(day);
  }

  return days;
};

// Update the calendar when the component is mounted
daysInMonth.value = getDaysInMonth(currentDate.value.getFullYear(), currentDate.value.getMonth());

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
  daysInMonth.value = getDaysInMonth(currentDate.value.getFullYear(), currentDate.value.getMonth());
  selectedDay.value = null; // Deselect the day when the month changes
  fetchWfhDates(); // Fetch WFH dates for the new month
};

const previousMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
  daysInMonth.value = getDaysInMonth(currentDate.value.getFullYear(), currentDate.value.getMonth());
  selectedDay.value = null; // Deselect the day when the month changes
  fetchWfhDates(); // Fetch WFH dates for the new month
};

const isToday = (day) => {
  const today = new Date();
  return (
    day === today.getDate() &&
    currentDate.value.getMonth() === today.getMonth() &&
    currentDate.value.getFullYear() === today.getFullYear()
  );
};

// Function to get WFH day status (0: grey, 1: green, 2: light red)
const getWfhDayStatus = (day) => {
  if (!day) return null; // Avoid empty days
  const dateString = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  // Find the date in the wfhDates array and return the status if found
  const found = wfhDates.value.find(wfh => wfh.date === dateString);
  return found ? found.status : null;
};

// Function to check if a day has a WFH request
const isWfhDay = (day) => {
  const status = getWfhDayStatus(day);
  return status !== null; // Show icon only for days with WFH requests (status 0, 1, or 2)
};

// Function to show the form when the plus button is clicked
const applyForWorkFromHome = (day) => {
  dayToConfirm.value = day; // Set the day to confirm
  showForm.value = true; // Show the WFH form
  reason.value = ''; // Clear the reason input
};

const confirmApplyWorkFromHome = async () => {
  const staffId = sessionStorage.getItem('staffID');
  if (!staffId) {
    alert('Error: Staff ID is missing');
    return;
  }

  const requestDate = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-${String(dayToConfirm.value).padStart(2, '0')}`;

  try {
    const response = await axios.post('http://localhost:6001/flexibleArrangement/createRequest', {
      staff_id: staffId,
      date: requestDate,
      reason: reason.value
    });

    if (response.status == 201) {
      alert('WFH request applied successfully!');
      fetchWfhDates(); // Refresh WFH dates
      showForm.value = false; // Close the form
    } else {
      alert('Something went wrong, please try again.');
    }
  } catch (error) {
    console.error('Error applying for WFH:', error);
    alert('Error: Unable to apply for WFH.');
  }
};

// Function to confirm withdrawal of a WFH request
const confirmWithdraw = async () => {
  let staffId = sessionStorage.getItem('staffID');
  staffId = parseInt(staffId, 10); // Convert staffId to an integer

  const dateToWithdraw = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-${String(dayToWithdraw.value).padStart(2, '0')}`;

  const pendingRequest = wfhDates.value.find(wfh => wfh.date === dateToWithdraw && wfh.status === 0);

  if (!pendingRequest) {
    alert('No pending request to withdraw');
    return;
  }

  const requestId = pendingRequest.request_id;

  try {
    const response = await axios.delete('http://localhost:6001/flexibleArrangement/withdrawRequest', {
      data: { staff_id: parseInt(staffId, 10), request_id: requestId } // Ensure staff_id is an integer
    });

    if (response.status == 200) {
      alert('Request withdrawn successfully!');
      fetchWfhDates(); // Refresh the WFH dates
    } else {
      alert('Something went wrong, please try again.');
    }
  } catch (error) {
    console.error('Error details:', error.response ? error.response.data : error.message);
    alert('Error: Unable to withdraw request. Please check the console for more details.');
  } finally {
    showWithdrawConfirmation.value = false; // Hide the confirmation popup
  }
};

// Show options popup for pending WFH requests
const showOptionsForWfh = (day) => {
  const dateString = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  
  // Find the WFH request for the selected day
  const wfhRequest = wfhDates.value.find(wfh => wfh.date === dateString);

  if (wfhRequest) {
    dayToWithdraw.value = wfhRequest.request_id;  // Set the correct request_id for withdrawal
    console.log('Request ID (from dayToWithdraw):', dayToWithdraw.value);  // Log the correct request_id
    showOptionsPopup.value = true;  // Show options popup
  } else {
    console.error('No WFH request found for the selected day');
  }
};

const withdrawWorkFromHome = async () => {
  const staffId = sessionStorage.getItem('staffID');
  const requestId = dayToWithdraw.value; // Get the request ID from the day selected

  if (!staffId || !requestId) {
    alert('Error: Staff ID or Request ID is missing');
    return;
  }

  try {
    // Send DELETE request to withdraw WFH request
    const response = await axios.delete('http://localhost:6001/flexibleArrangement/withdrawRequest', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        staff_id: parseInt(staffId, 10), // Ensure staff_id is sent as an integer
        request_id: requestId // Send the request_id
      }
    });

    if (response.status === 200) {
      alert('Request withdrawn successfully!');
      fetchWfhDates(); // Refresh the WFH dates after successful deletion
    } else {
      alert('Something went wrong, please try again.');
    }
  } catch (error) {
    console.error('Error withdrawing WFH request:', error.response ? error.response.data : error.message);
    alert('Error: Unable to withdraw request. Please check the console for more details.');
  } finally {
    // Close both confirmation and options popup regardless of success or failure
    showWithdrawConfirmation.value = false;
    showOptionsPopup.value = false; // If there is another popup open, also ensure it is closed
  }
};

const fetchWfhDates = async () => {
  const staffId = sessionStorage.getItem('staffID');

  if (!staffId) {
    alert('Error: Staff ID is missing');
    return;
  }

  const url = `http://localhost:6001/flexibleArrangement/ownRequests/${staffId}`;

  try {
    const response = await axios.get(url);

    // Check if response is 200 and contains data
    if (response.status === 200 && response.data.length > 0) {
      wfhDates.value = response.data.map(req => {
        const parsedDate = new Date(req.Date);
        const formattedDate = `${parsedDate.getFullYear()}-${String(parsedDate.getMonth() + 1).padStart(2, '0')}-${String(parsedDate.getDate()).padStart(2, '0')}`;
        return {
          date: formattedDate,
          status: req.Status,
          request_id: req.Request_ID // Store the request ID for withdrawal
        };
      });
      console.log('WFH Dates:', wfhDates.value);
    } else {
      // If no data, clear the wfhDates array
      wfhDates.value = [];
      console.log('No WFH requests found');
    }
  } catch (error) {
    if (error.response && error.response.status === 404) {
      // Handle 404 error for no requests found
      wfhDates.value = [];
      console.log('No WFH requests found');
    } else {
      console.error('Error fetching WFH dates:', error);
      alert('Error: Unable to fetch WFH dates.');
    }
  }
};

const cancelWorkFromHome = () => {
  showForm.value = false; // Hide the form
};



const changeWfhDate = async () => {
  const staffId = parseInt(sessionStorage.getItem('staffID'), 10);  // Get staff ID from session
  if (!staffId) {
    alert('Error: Staff ID is missing');
    return;
  }

  // Get the request ID and the original requested date
  const requestId = dayToWithdraw.value; // Assuming you have requestId stored here

  // Find the initial WFH requested date for the current request
  const initialRequest = wfhDates.value.find(wfh => wfh.request_id === requestId);
  const initialDate = initialRequest ? initialRequest.date : null;

  if (!initialDate) {
    alert('Error: Unable to retrieve initial WFH request date.');
    return;
  }

  let isValidDate = false;
  let newDate = null;

  // Keep asking for a valid and different date until the user enters a correct one or cancels
  while (!isValidDate) {
    newDate = prompt('Enter a new date for WFH (YYYY-MM-DD):');

    if (!newDate) {
      // If the user presses "Cancel", close the popup
      showOptionsPopup.value = false;
      return;
    }

    const dateRegex = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;

    if (!dateRegex.test(newDate)) {
      alert('Invalid date format! Please enter a valid date in YYYY-MM-DD format (with correct month and day).');
    } else if (newDate === initialDate) {
      alert('The new date cannot be the same as the original requested date. Please choose a different date.');
    } else {
      const dateInput = new Date(newDate);
      const currentDate = new Date();

      // Check if the date is at least 24 hours in the future
      if (dateInput.getTime() - currentDate.getTime() < 24 * 60 * 60 * 1000) {
        alert('Date must be at least 24 hours from now. Please enter a valid future date.');
      } else {
        isValidDate = true;  // Mark the date as valid if all checks pass and it's different from the original date
      }
    }
  }

  // Persistent prompt for reason
  let newReason = '';
  while (!newReason) {
    newReason = prompt('Enter a new reason for WFH:', reason.value || '');
    if (!newReason) {
      alert('A reason is required. Please enter a valid reason.');
    }
  }

  try {
    // Send the PUT request to the backend to update the WFH request
    const response = await axios.put('http://localhost:6001/flexibleArrangement/updateRequest', {
      staff_id: staffId,
      request_id: requestId,
      date: newDate,
      reason: newReason
    });

    if (response.status === 200) {
      alert('WFH request updated successfully!');
      fetchWfhDates();  // Refresh WFH dates after update
    } else {
      alert('Something went wrong. Please try again.');
    }
  } catch (error) {
    console.error('Error updating WFH request:', error.response ? error.response.data : error.message);
    alert('Error: Unable to update WFH request.');
  } finally {
    showOptionsPopup.value = false;  // Close the options popup after successful submission
  }
};



const closePopup = () => {
  showOptionsPopup.value = false; // Close the popup
};


// Fetch WFH dates when the component is mounted
onMounted(fetchWfhDates);
</script>


<template>
  <div>
    <NavBar></NavBar>
    <div class="container-fluid">
      <div class="row text-center justify-content-center">
        <div class="col-12 header-container">
          <h3 class="mb-3">My Schedule</h3>
        </div>

        <!-- Flexbox Container for Side-by-Side Layout -->
        <div class="col-12 d-flex calendar-form-container">
          <div class="calendar-container">
            <div class="calendar card shadow-sm">
              <!-- Calendar Header -->
              <div class="calendar-header d-flex justify-content-between align-items-center p-3">
                <button class="btn btn-outline-primary" @click="previousMonth">
                  <i class="bi bi-arrow-left-circle"></i> Previous
                </button>
                <h4 class="m-0">{{ currentDate.toLocaleString('default', { month: 'long' }) }} {{
                  currentDate.getFullYear() }}</h4>
                <button class="btn btn-outline-primary" @click="nextMonth">
                  Next <i class="bi bi-arrow-right-circle"></i>
                </button>
              </div>

              <!-- Calendar Grid -->
              <div class="calendar-grid p-2">
                <div class="calendar-day fw-bold text-center" v-for="day in daysOfWeek" :key="day">{{ day }}</div>
                <div v-for="(day, index) in daysInMonth" :key="index" class="calendar-cell text-center"
                  @mouseover="hoveredDay = day" @mouseleave="hoveredDay = null" :class="{
                    'empty-day': day === '',
                    'selected-day': day === selectedDay,
                    today: isToday(day),
                    'wfh-day-grey': getWfhDayStatus(day) === 0,
                    'wfh-day-green': getWfhDayStatus(day) === 1,
                    'wfh-day-red': getWfhDayStatus(day) === 2,
                  }">
                  <span v-if="day">{{ day }}</span>

                  <!-- "+" Button appears on hover, but only if there's no existing WFH request -->
                  <button v-if="hoveredDay === day && day !== '' && !isWfhDay(day)" class="apply-btn"
                    @click.stop="applyForWorkFromHome(day)">+</button>

                  <!-- Pencil icon for pending WFH requests (shown only on hover) -->
                  <i v-if="getWfhDayStatus(day) === 0 && hoveredDay === day" class="bi bi-pencil-fill edit-icon"
                    @click.stop="showOptionsForWfh(day)"></i>

                  <!-- WFH icon or badge, shown only for days with requests (status 0, 1, or 2) -->
                  <i v-if="isWfhDay(day)" class="bi bi-house-fill wfh-icon"></i>
                </div>
              </div>

              <!-- Legend for WFH status inside the calendar -->
              <div class="calendar-legend mt-3 p-2 d-flex justify-content-around">
                <div class="legend-item">
                  <span class="legend-box pending"></span> Pending
                </div>
                <div class="legend-item">
                  <span class="legend-box approved"></span> Approved
                </div>
                <div class="legend-item">
                  <span class="legend-box denied"></span> Denied
                </div>
              </div>
            </div>
          </div>

          <!-- Inline WFH Form (Side by Side with Calendar) -->
          <div v-if="showForm" class="wfh-form">
            <h5>Apply for Work From Home</h5>
            <p>Date: {{ dayToConfirm }} {{ currentDate.toLocaleString('default', { month: 'long' }) }}</p>
            <div class="form-group">
              <label for="reason">Reason for WFH:</label>
              <input type="text" v-model="reason" id="reason" class="form-control" placeholder="Enter your reason" />
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" @click="confirmApplyWorkFromHome">Confirm</button>
              <button class="btn btn-secondary" @click="cancelWorkFromHome">Cancel</button>
            </div>
          </div>

          <!-- Options popup for WFH request -->
          <div v-if="showOptionsPopup" class="options-popup">
            <!-- Close Button (X) -->
            <button class="close-btn" @click="closePopup">×</button>

            <p>Select an action for WFH Request:</p>
            <div class="form-actions">
              <button class="btn btn-primary" @click="changeWfhDate">Change WFH Date</button>
              <button class="btn btn-danger" @click="withdrawWorkFromHome">Delete WFH Request</button>
            </div>
          </div>

          <!-- Confirmation popup for withdrawing WFH request -->
          <div v-if="showWithdrawConfirmation" class="withdraw-confirmation">
            <p>Confirm to Withdraw WFH Request?</p>
            <div class="form-actions">
              <button class="btn btn-primary" @click="confirmWithdraw">Confirm</button>
              <button class="btn btn-secondary" @click="showWithdrawConfirmation = false">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-container {
  margin-top: 20px;
  padding-bottom: 10px;
}

.calendar-form-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-top: 20px;
}

.calendar-container {
  flex: 3;
  max-width: 1000px;
  margin: 0 auto;
}

.wfh-form {
  flex: 1;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  margin-left: 20px;
}

.calendar {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 10px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  width: 100%;
}

.calendar-cell {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  background-color: white;
  position: relative;
  transition: background-color 0.3s ease;
}

.calendar-cell.selected-day {
  background-color: #e2e3e5;
  color: #495057;
  font-weight: bold;
  border-radius: 8px;
  border: 2px solid #495057;
}

.calendar-cell.today {
  background-color: #d1e7ff;
  color: #0d6efd;
  font-weight: bold;
  border-radius: 8px;
  border: 1px solid #0d6efd;
}

.calendar-cell.wfh-day-grey {
  background-color: #e2e3e5;
  border: 2px solid #0d6efd;
}

.calendar-cell.wfh-day-green {
  background-color: #d1ffd1;
  border: 2px solid #0d6efd;
}

.calendar-cell.wfh-day-red {
  background-color: #ffd1d1;
  border: 2px solid #0d6efd;
}

.calendar-cell:hover {
  background-color: #f8f9fa;
  transition: background-color 0.3s ease;
}

.apply-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: #0d6efd;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 10px;
  cursor: pointer;
}

.edit-icon {
  position: absolute;
  top: 5px;
  left: 5px;
  font-size: 16px;
  cursor: pointer;
  color: #0d6efd;
}

.wfh-icon {
  position: absolute;
  bottom: 5px;
  right: 5px;
  font-size: 18px;
  color: #0d6efd;
}

.form-group {
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ced4da;
}

.form-actions {
  display: flex;
  justify-content: space-around;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
}

.btn-primary {
  background-color: #0d6efd;
  color: white;
  border: none;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
}

/* Adjusting the flex container to align items side by side */
.calendar-form-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-top: 20px;
}

.calendar {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

/* Legend styles inside the calendar with flexbox for side-by-side alignment */
.calendar-legend {
  background-color: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  padding: 10px;
  text-align: left;
  display: flex;
  justify-content: space-around;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 10px;
}

.legend-box {
  width: 20px;
  height: 20px;
  margin-right: 5px;
  border-radius: 3px;
}

.legend-box.pending {
  background-color: #e2e3e5;
}

.legend-box.approved {
  background-color: #d1ffd1;
}

.legend-box.denied {
  background-color: #ffd1d1;
}

/* Options popup styles */
.options-popup {
  padding: 20px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
}

.withdraw-confirmation {
  padding: 20px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
}

.form-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #000;
}

.close-btn:hover {
  color: red;
}

</style>