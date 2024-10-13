import mysql.connector
from flask import Flask, request, jsonify
from os import environ
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ** Database connection configuration
    db_config = {
        'host': environ.get('DB_HOST'),
        'user': environ.get('DB_USER'),
        'password': environ.get('DB_PASSWORD'),
        'port': environ.get('DB_PORT'),
        'database': environ.get('DB_NAME')
        # 'host': 'localhost',
        # 'user': 'root',
        # 'password': 'root',
        # 'port': '3301',
        # 'database': 'account'
    }

    # ** Get all users (READ) with parameters for filtering
    @app.route('/users', methods=['GET'])
    def get_users():
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # ** Extract the parameters from the query string
            dept = request.args.get('dept')
            position = request.args.get('position')
            country = request.args.get('country')
            role = request.args.get('role')
            Reporting_Manager = request.args.get('Reporting_Manager')

            # ** paginate
            page = request.args.get('page')
            page_size = request.args.get('page_size')

            # ** Construct the query based on the parameters
            query = 'SELECT Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role FROM Employee WHERE 1=1'
            if dept:
                query += f" AND Dept = '{dept}'"
            if position:
                query += f" AND Position = '{position}'"
            if country:
                query += f" AND Country = '{country}'"
            if role:
                query += f" AND Role = {role}"
            if Reporting_Manager:
                query += f" AND Reporting_Manager = {Reporting_Manager}"
            if page and page_size:
                offset = (int(page) - 1) * int(page_size)
                query += f" LIMIT {page_size} OFFSET {offset}"

            # ** Execute the query
            cursor.execute(query)
            users = cursor.fetchall()

            # ** close the cursor and connection
            cursor.close()
            conn.close()

            return jsonify(users), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ** Get a single user by ID (READ)
    @app.route('/user/<int:staff_id>', methods=['GET'])
    def get_user(staff_id):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role
                FROM Employee
                WHERE Staff_ID = %s
            ''', (staff_id,))

            # ** Fetch the user
            user = cursor.fetchone()

            # ** close the cursor and connection
            cursor.close()
            conn.close()
            if user:
                return jsonify(user), 200
            else:
                return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ** retrieve by batch of users
    @app.route('/users/batch', methods=['GET'])
    def get_users_batch():
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            data = request.get_json()
            staff_ids = data['staff_ids']

            # ** Construct the query based on the parameters
            query = 'SELECT Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role FROM Employee WHERE Staff_ID IN ('
            query += ', '.join([str(id) for id in staff_ids])
            query += ')'

            # ** Execute the query
            cursor.execute(query)
            users = cursor.fetchall()

            # ** close the cursor and connection
            cursor.close()
            conn.close()

            return jsonify(users), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ** login to the system
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()

        staffID = data['staffID']
        password = data['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role
            FROM Employee
            WHERE Staff_ID = %s AND Password = %s
        ''', (staffID, password))

        # ** Fetch the user
        user = cursor.fetchone()

        # ** close the cursor and connection
        cursor.close()
        conn.close()

        if user:
            return jsonify(user), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    # ** retrieve all departments
    @app.route('/departments', methods=['GET'])
    def get_departments():
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT Dept FROM Employee')

            # ** Fetch all departments
            departments = cursor.fetchall()

            # ** close the cursor and connection
            cursor.close()
            conn.close()

            return jsonify(departments), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)