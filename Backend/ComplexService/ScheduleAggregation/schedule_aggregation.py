import requests
import mysql.connector
import json
from flask import Flask, request, jsonify
from os import environ
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Microservice URL configurations
ACCOUNTS_SERVICE_URL = "http://host.docker.internal:5001"
SCHEDULE_SERVICE_URL = "http://host.docker.internal:5002"

# Schedule aggregation based on type (team, department, or all)
@app.route('/aggregateSchedule', methods=['GET'])
def aggregate_schedules():
    schedule_type = request.args.get('type')  # Type of schedule (team, dept, all)
    staff_id = request.args.get('staff_id')   # Get login user info
    position = get_user_position(staff_id)    # Getting user position
    dept = request.args.get('dept')           # Optional, for dept aggregation
    reporting_manager = request.args.get('reporting_manager')  # Optional, for team
    start_date = request.args.get('start_date')  # Date or Date_range (default to current month)
    end_date = request.args.get('end_date')

    # Validate the date range
    start_date, end_date, error = validate_date_range(start_date, end_date)
    if error:
        return jsonify({'error': error}), 400

    # Schedule Type Checks
    if schedule_type == "Single":
        if not staff_id:
            return jsonify({'error': 'Staff ID not found'}), 400
        
        schedules = get_schedule_by_staff_id(staff_id, start_date, end_date)
        print(f"Schedule service response: {schedules}")  # Output the schedule service response
            
    elif schedule_type == 'Team':
        if not reporting_manager:
            return jsonify({'error': 'Reporting Manager is required for team-based aggregation'}), 400
        staff_ids = get_staff_ids_by_team(reporting_manager)
        schedules = get_schedules_by_staff_ids(staff_ids, start_date, end_date)
        print(f"Schedule service response: {schedules}")  # Output the schedule service response

    elif schedule_type == 'Dept':
        if not dept:
            return jsonify({'error': 'Department is required for department-based aggregation'}), 400
        staff_ids = get_staff_ids_by_department(dept)
        schedules = get_schedules_by_staff_ids(staff_ids, start_date, end_date)
        print(f"Schedule service response: {schedules}")  # Output the schedule service response

    elif schedule_type == 'All':
        # Validate role for "All" type schedules: Only allow HR and Directors
        if not validate_position(position):
            return jsonify({'error': 'Unauthorized access: Only HR or Directors can access all schedules'}), 403
        schedules = get_all_schedules(start_date, end_date)
        print(f"Schedule service response: {schedules}")  # Output the schedule service response

    # Initialize lists to collect original and augmented schedules
    original_schedules = []   # This will store the original schedules
    augmented_schedules = []  # This will store the schedules after augmentation with user data

    # Check if schedules exist
    if not schedules or len(schedules) == 0:
        return jsonify({"error": "No schedules found"}), 404

    # Loop through the original schedules to augment them
    for schedule in schedules:
        if not isinstance(schedule, dict):
            print(f"Unexpected schedule format: {schedule}, type: {type(schedule)}")
            continue  # Skip invalid schedules

        original_schedules.append(schedule.copy())  # Store the original schedule

        staff_id = schedule['Staff_ID']
        try:
            print(f"Fetching data for Staff_ID: {staff_id}")  # Debugging print statement
            response = requests.get(f"{ACCOUNTS_SERVICE_URL}/user/{staff_id}")
            print(f"Account service response for Staff_ID {staff_id}: {response.text}")  # Output account service response
            response.raise_for_status()
            user_data = response.json()

            if not user_data:
                print(f"No user data found for Staff_ID: {staff_id}")  # Debugging print

            # Augment schedule data with user info
            augmented_schedule = schedule.copy()  # Create a copy to augment
            augmented_schedule.update({
                'Staff_FName': user_data.get('Staff_FName', 'Unknown'),
                'Staff_LName': user_data.get('Staff_LName', 'Unknown'),
                'Dept': user_data.get('Dept', 'Unknown'),
                'Email': user_data.get('Email', 'Unknown'),
                'Position': user_data.get('Position', 'Unknown'),
                'Country': user_data.get('Country', 'Unknown'),
                'Role': user_data.get('Role', 'Unknown'),
                'Reporting_Manager': user_data.get('Reporting_Manager', 'Unknown')
            })

            augmented_schedules.append(augmented_schedule)

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving user data for Staff_ID {staff_id}: {e}")
            # Handle error by appending the original schedule without augmentation
            augmented_schedules.append(schedule.copy())

    # Combine the original and augmented schedules for comparison
    combined_response = {
        "original_schedules": original_schedules,
        "augmented_schedules": augmented_schedules
    }

    # Return the combined response  
    return jsonify(combined_response), 200


# Utility function to validate date format
def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Helper function to validate date range and handle default if needed
def validate_date_range(start_date, end_date):
    try:
        # If no dates are provided, use the first and last day of the current month
        if not start_date and not end_date:
            today = datetime.today()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')

        # Validate provided date formats
        if start_date and not validate_date(start_date):
            return None, None, "Invalid start date format. Please use 'YYYY-MM-DD'."
        if end_date and not validate_date(end_date):
            return None, None, "Invalid end date format. Please use 'YYYY-MM-DD'."

        # Check if the start date is after the end date
        if start_date and end_date and datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
            return None, None, "Start date cannot be after end date."

    except ValueError as e:
        return None, None, str(e)

    return start_date, end_date, None

# Helper function to validate user position for viewing all schedules (only allow HR and Directors)
def validate_position(position):
    # Check if the user's position is "HR Team" or "Director"
    if position == 'HR Team' or position == 'Director' or position == "MD":
        return True
    return False

# Helper function to get the user's position from the accounts microservice
def get_user_position(staff_id):
    try:
        # Call the accounts microservice to get user details
        response = requests.get(f"{ACCOUNTS_SERVICE_URL}/user/{staff_id}")
        print(response.text)  # Log the response body
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        
        user_data = response.json()

        # Extract the user's position from the response
        if 'Position' in user_data:
            return user_data['Position']
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving user position for staff_id {staff_id}: {e}")
        return None


def get_schedule_by_staff_id(staff_id,start_date,end_date):
    
    try:
        response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/personal/{staff_id}?start_date={start_date}&end_date={end_date}")
        print(response.text)  # Log the response body
        response.raise_for_status()

        schedule = response.json()  
        
        return schedule
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving schedule")
        return []

# Helper function to get staff IDs by department
def get_staff_ids_by_department(department):
    try:
        response = requests.get(f"{ACCOUNTS_SERVICE_URL}/users?dept={department}")
        print(response.text)  # Log the response body
        response.raise_for_status()
        
        # Assuming the response is a list of users
        users = response.json()
        
        # Extract staff IDs from the list
        staff_ids = [user['Staff_ID'] for user in users]
        return staff_ids
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving staff IDs for department {department}: {e}")
        return []


# Helper function to get staff IDs by team (reporting manager)
def get_staff_ids_by_team(reporting_manager):
    try:
        response = requests.get(f"{ACCOUNTS_SERVICE_URL}/users?Reporting_Manager={reporting_manager}")
        print(response.text)  # Log the response body
        response.raise_for_status()
        
        # Assuming the response is a list of users
        users = response.json()
        
        # Extract staff IDs from the list
        staff_ids = [user['Staff_ID'] for user in users]
        print(f"Staff ids are {staff_ids} ")
        return staff_ids
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving staff IDs for team {reporting_manager}: {e}")
        return []
    


# Helper function to get schedules by staff_ids under reporting manager (reporting manager)
def get_schedules_by_staff_ids(staff_ids,start_date,end_date):
    try:
        # Convert list of staff_ids into a comma-separated string so that can pass as param
        staff_ids = ','.join(map(str, staff_ids))
        response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/group?staff_ids={staff_ids}&start_date={start_date}&end_date={end_date}")
        print(response.text)  # Log the response body
        response.raise_for_status()

        schedules = response.json()  
        
        return schedules
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving schedule")
        return []

# Helper function to get all schedules with date filtering
def get_all_schedules(start_date, end_date):
    try:
        response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/organisation?start_date={start_date}&end_date={end_date}")
        print(response.text)  # Log the response body
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to retrieve all schedules: {str(e)}'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6003, debug=True)
