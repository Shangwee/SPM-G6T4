import requests
from flask import Flask, request, jsonify
from os import environ
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Microservice URL configurations
# TODO:Change this later 
ACCOUNTS_SERVICE_URL = "http://host.docker.internal:5001"
SCHEDULE_SERVICE_URL = "http://host.docker.internal:5002"

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

# Schedule aggregation based on type (team, department, or all)
@app.route('/aggregateSchedule', methods=['GET'])
def aggregate_schedules():
    schedule_type = request.args.get('type')  # Type of schedule (team, dept, all)
    staff_id = request.args.get('staff_id')   # Get login user info
    position = get_user_position(staff_id)    # Getting user position
    dept = request.args.get('dept')           # Optional, for dept aggregation
    reporting_manager = request.args.get('Reporting_Manager')  # Optional, for team
    start_date = request.args.get('start_date')  # Date or Date_range (default to current month)
    end_date = request.args.get('end_date')

    # Validate the date range
    start_date, end_date, error = validate_date_range(start_date, end_date)
    if error:
        return jsonify({'error': error}), 400

    # Schedule Type Checks
    if schedule_type == 'Team':
        if not reporting_manager:
            return jsonify({'error': 'Reporting Manager is required for team-based aggregation'}), 400
        schedules = get_schedules_by_team(reporting_manager, start_date, end_date)

    elif schedule_type == 'Dept':
        if not dept:
            return jsonify({'error': 'Department is required for department-based aggregation'}), 400
        schedules = get_schedules_by_department(dept, start_date, end_date)

    elif schedule_type == 'All':
        # Validate role for "All" type schedules: Only allow HR and Directors
        if not validate_position(position):
            return jsonify({'error': 'Unauthorized access: Only HR or Directors can access all schedules'}), 403
        schedules = get_all_schedules(start_date, end_date)
        # get all members from accounts microservice
        for schedule in schedules:
            staff_id = schedule['Staff_ID']
            response = requests.get(f"{ACCOUNTS_SERVICE_URL}/user/{staff_id}")
            response.raise_for_status()
            user_data = response.json()
            schedule['Staff_FName'] = user_data['Staff_FName']
            schedule['Staff_LName'] = user_data['Staff_LName']
            schedule['Dept'] = user_data['Dept']
            schedule['Email'] = user_data['Email']
            schedule['Position'] = user_data['Position']
            schedule['Country'] = user_data['Country']
            schedule['Role'] = user_data['Role']
            schedule['Reporting_Manager'] = user_data['Reporting_Manager']
        # combine the schedules with the members

    else:
        return jsonify({'error': 'Invalid schedule type'}), 400

    return jsonify(schedules), 200

# Helper function to validate user position (only allow HR and Directors)
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
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        
        user_data = response.json()

        # Extract the user's position from the response
        if 'Position' in user_data:
            return user_data['Position']
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving user position for staff_id {staff_id}: {e}")
        return None

# Helper function to get schedules by department with date filtering
def get_schedules_by_department(department, start_date, end_date):
    try:
        response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/dept/{department}?start_date={start_date}&end_date={end_date}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to retrieve department schedules: {str(e)}'}

# Helper function to get schedules by team with date filtering
def get_schedules_by_team(reporting_manager, start_date, end_date):
    try:
        response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/team/{reporting_manager}?start_date={start_date}&end_date={end_date}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to retrieve team schedules: {str(e)}'}

# Helper function to get all schedules with date filtering
def get_all_schedules(start_date, end_date):
    try:
        response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/organisation?start_date={start_date}&end_date={end_date}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to retrieve all schedules: {str(e)}'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6003, debug=True)
