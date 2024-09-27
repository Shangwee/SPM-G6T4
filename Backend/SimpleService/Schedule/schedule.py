import mysql.connector
import requests
from flask import Flask, request, jsonify
from os import environ
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database connection configuration
db_config = {
    'host': environ.get('DB_HOST'),
    'user': environ.get('DB_USER'),
    'password': environ.get('DB_PASSWORD'),
    'port': environ.get('DB_PORT'),
    'database': environ.get('DB_NAME')
}

# Utility function to validate date format
def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Utility function to apply date filters to a query
def apply_date_filters(query, parameters, start_date, end_date):
    if start_date and end_date:
        query += " AND Date BETWEEN %s AND %s"
        parameters += (start_date, end_date)
    elif start_date:
        query += " AND Date >= %s"
        parameters += (start_date,)
    elif end_date:
        query += " AND Date <= %s"
        parameters += (end_date,)
    return query, parameters

# Reusable function to execute a query and return the results
def execute_query(query, parameters=()):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, parameters)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# Create new schedule (Create)
@app.route('/schedule', methods=['POST'])
def create_schedule():
    data = request.get_json()
    
    staff_id = data.get("staff_id")
    request_id = data.get("request_id")
    date = data.get("date")

    if not staff_id or not request_id or not date or not validate_date(date):
        return jsonify({'error': 'Please provide valid staff_id, request_id, and date (YYYY-MM-DD)'}), 400
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Schedule (Staff_ID, Request_ID, Date)
            VALUES (%s, %s, %s)
        ''', (staff_id, request_id, date))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Schedule created successfully'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'message': 'Schedule already exists'}), 409

# Get all schedules (Read) with optional date filtering
@app.route('/schedule/organisation', methods=['GET'])
def get_schedules():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Validate dates if provided
    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

    query = "SELECT * FROM Schedule WHERE 1=1"
    parameters = ()
    query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    schedules = execute_query(query, parameters)
    return jsonify(schedules), 200

# Get schedule by staff_id with optional date filtering
@app.route('/schedule/personal/<int:staff_id>', methods=['GET'])
def get_own_schedule(staff_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

    query = "SELECT * FROM Schedule WHERE Staff_ID = %s"
    parameters = (staff_id,)
    query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    schedules = execute_query(query, parameters)
    return jsonify(schedules), 200

# Get schedules by team with optional date filtering
@app.route('/schedule/team/<string:team>', methods=['GET'])
def get_team_schedule(team):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

    staff_ids = get_staff_ids_by_team(team)
    if not staff_ids:
        return jsonify({'error': 'Unable to retrieve team information'}), 500

    query = "SELECT * FROM Schedule WHERE Staff_ID IN (%s)" % ','.join(['%s'] * len(staff_ids))
    parameters = tuple(staff_ids)
    query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    schedules = execute_query(query, parameters)
    return jsonify(schedules), 200

# Get schedules by department with optional date filtering
@app.route('/schedule/dept/<string:department>', methods=['GET'])
def get_department_schedule(department):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

    staff_ids = get_staff_ids_by_department(department)
    if not staff_ids:
        return jsonify({'error': 'Unable to retrieve department information'}), 500

    query = "SELECT * FROM Schedule WHERE Staff_ID IN (%s)" % ','.join(['%s'] * len(staff_ids))
    parameters = tuple(staff_ids)
    query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    schedules = execute_query(query, parameters)
    return jsonify(schedules), 200

# Function to get staff IDs by department from the accounts microservice
def get_staff_ids_by_department(department):
    try:
        response = requests.get(f"http://account:5000/users?dept={department}")
        response.raise_for_status()
        users = response.json().get('users', [])
        staff_ids = [user['Staff_ID'] for user in users]
        return staff_ids
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving staff IDs for department {department}: {e}")
        return None

# Function to get staff IDs by team from the accounts microservice
def get_staff_ids_by_team(team):
    try:
        response = requests.get(f"http://account:5000/users?Reporting_Manager={team}")
        response.raise_for_status()
        users = response.json().get('users', [])
        staff_ids = [user['Staff_ID'] for user in users]
        return staff_ids
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving staff IDs for team {team}: {e}")
        return None
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)