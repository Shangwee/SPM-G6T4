import mysql.connector
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


# Create new schedule (Create) TODO:Change date to use current datetime. need some logic to standardise the time set for various timezones
@app.route('/schedule', methods=['POST'])
def create_schedule():
    data = request.get_json()
    
    staff_id = data.get("staff_id")
    request_id = data.get("request_id")
    date = data.get("date") 

    if not staff_id or not request_id or not date or not validate_date_range(date,date):
        return jsonify({'error': 'Please provide valid staff_id, request_id, and date (YYYY-MM-DD)'}), 400
    
    #check if the staff_id and request_id exist in the database
    if check_staff_request_exists(staff_id, request_id):
        return jsonify({'error': 'Schedule already exists'}), 409
    
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


# Delete schedule by schedule_ID
@app.route('/schedule/delete/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Checking if the schedule exists
        cursor.execute("SELECT * FROM Schedule WHERE Schedule_ID = %s", (schedule_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Schedule not found'}), 404

        # Delete the schedule
        cursor.execute("DELETE FROM Schedule WHERE Schedule_ID = %s", (schedule_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': f'Schedule {schedule_id} deleted successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500




# Get all schedules with optional date filtering
@app.route('/schedule/organisation', methods=['GET'])
def get_schedules():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Validate date range
    error, status_code = validate_date_range(start_date, end_date)
    if error:
        return jsonify(error), status_code

    query = "SELECT * FROM Schedule WHERE 1=1"
    parameters = []

    # Apply date filters if provided
    if start_date or end_date:
        query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    # Debugging: Log the final query and parameters
    print(f"Final Query: {query}")
    print(f"Parameters: {parameters}")

    # Execute query and return results
    schedules = execute_query(query, tuple(parameters))  # Ensure parameters are passed as tuple
    return jsonify(schedules), 200



# Get schedule by staff_id with optional date filtering 
@app.route('/schedule/personal/<int:staff_id>', methods=['GET'])
def get_own_schedule(staff_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Validate date range
    error, status_code = validate_date_range(start_date, end_date)
    if error:
        return jsonify(error), status_code

    query = "SELECT * FROM Schedule WHERE Staff_ID = %s"
    parameters = (staff_id,)
    query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    schedules = execute_query(query, parameters)
    return jsonify(schedules), 200


# Get schedules based on passed staff IDs 
@app.route('/schedule/group', methods=['GET'])
def get_team_schedule():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    staff_ids = request.args.get('staff_ids')  # Passed in as a list of staff IDs

    # Split staff_ids by comma and strip whitespace
    staff_ids = request.args.get('staff_ids', '').split(',')
    staff_ids = [staff_id.strip() for staff_id in staff_ids if staff_id.strip()]  # Remove empty IDs

    if not staff_ids:
        return jsonify({'error': 'No staff IDs provided'}), 400

    # Validate date range
    error, status_code = validate_date_range(start_date, end_date)
    if error:
        return jsonify(error), status_code

    query = "SELECT * FROM Schedule WHERE Staff_ID IN (%s)" % ','.join(['%s'] * len(staff_ids))
    parameters = tuple(staff_ids)
    query, parameters = apply_date_filters(query, parameters, start_date, end_date)

    schedules = execute_query(query, parameters)
    return jsonify(schedules), 200


# Function to check if staff_id and request_id exist in the database
def check_staff_request_exists(staff_id, request_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Schedule WHERE Staff_ID = %s AND Request_ID = %s''', (staff_id, request_id))
    
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

# Utility function to validate date format and check if start_date is after end_date
def validate_date_range(start_date, end_date):
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                return {'error': 'Invalid date range: start date is after end date'}, 400
        except ValueError:
            return {'error': 'Invalid date format, use YYYY-MM-DD'}, 400
    elif start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return {'error': 'Invalid start date format, use YYYY-MM-DD'}, 400
    elif end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return {'error': 'Invalid end date format, use YYYY-MM-DD'}, 400

    return None, None  # If everything is valid


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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
