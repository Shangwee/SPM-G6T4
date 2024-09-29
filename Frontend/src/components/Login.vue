<template>
    <div class="full-screen-container">
        <div class="card-container">
            <div class="login-section">
                <form @submit.prevent="login">
                    <h2>Login</h2>
                    <div class="input-group">
                        <label for="staffID">Staff ID</label>
                        <input type="text" id="staffID" v-model="credentials.staffID" required>
                    </div>
                    <div class="input-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" v-model="credentials.password" required>
                    </div>
                    <button type="submit">Login</button>

                    <!-- Error popup -->
                    <div v-if="errorMessage" class="error-popup">
                        {{ errorMessage }}
                    </div>
                </form>
            </div>
            <div class="text-section">
                <div class="border rounded-3 border-2 border-light p-2 bg-opacity-75 bg-white">
                    <h2>Welcome to Work-From-Home Management System</h2>
                    <p>Enter your login details to start accessing.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            credentials: {
                staffID: '',
                password: ''
            },
            errorMessage: '' // Initialize as empty
        };
    },
    methods: {
        async login() {
            try {
                // Reset the error message before trying login
                this.errorMessage = '';

                const response = await fetch('http://localhost:5001/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.credentials),
                });

                const data = await response.json();

                if (response.ok) {
                    // Successful login
                    sessionStorage.setItem('staffID', data.Staff_ID);
                    sessionStorage.setItem('role', data.Role);

                    // Redirect user to the homepage or dashboard
                    this.$router.push('/');
                } else {
                    // Display error message from response
                    this.errorMessage = data.message || 'Incorrect login details, please try again.';
                }
            } catch (error) {
                // Catch any network or server errors
                this.errorMessage = 'Login failed, please try again later.';
            }
        },
    },
};
</script>

<style scoped>
.full-screen-container {
    display: flex;
    justify-content: center;
    margin-top: 200px;
}

.card-container {
    display: flex;
    width: 900px;
    height: 500px;
    box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.2);
    border-radius: 20px;
    overflow: hidden;
}

.login-section,
.text-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 40px;
}

.login-section {
    background-color: #fff;
}

.text-section {
    background-image: url('../assets/94999.png');
    background-size: contain;
}

.input-group input {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

button {
    padding: 10px;
    border: none;
    border-radius: 4px;
    background-color: #5c6bc0;
    color: white;
    cursor: pointer;
}

button:hover {
    background-color: #3f51b5;
}

/* Error popup styles */
.error-popup {
    margin-top: 10px;
    padding: 10px;
    color: white;
    background-color: red;
    border-radius: 4px;
    text-align: center;
    animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}
</style>
