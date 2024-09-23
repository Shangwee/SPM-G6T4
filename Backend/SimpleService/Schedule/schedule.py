import mysql.connector
import requests
from flask import Flask, request, jsonify
from os import environ
from flask_cors import CORS

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

# Create new schedule (Create)
@app.route('/schedule', methods=['POST'])
def create_schedule():
    data = request.get_json()

    staff_id = data["staff_id"]
    request_id = data["request_id"]
    date = data["date"]

    if not staff_id or not request_id or not date:
        return jsonify({'error': 'Please provide all the required fields'}), 400
    
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


# Get all schedules (Read)
@app.route('/schedule', methods=['GET'])
def get_schedules():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT * FROM Schedule")
    cursor.execute(query)

    schedules = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(schedules), 200

# Delete schedule by schedule_id (Delete)
@app.route('/schedule/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Schedule
        WHERE Schedule_ID = %s
    ''', (schedule_id,))

    conn.commit()
    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({'message': 'Schedule not found'}), 404

    return jsonify({'message': 'Schedule deleted successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)