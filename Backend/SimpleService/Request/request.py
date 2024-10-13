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

# ** get all requests (add filters)
@app.route('/request', methods=['GET'])
def get_request():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT Request_ID, Employee_ID, Approver_ID, Date, Reason, Status FROM Request where 1=1")

    # ** Extract the parameters from the query string
    Employee_ID = request.args.get('Employee_ID')
    Approver_ID = request.args.get('Approver_ID')
    Status = request.args.get('Status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # ** pagination parameters
    page = request.args.get('page')
    page_size = request.args.get('page_size')


    if Employee_ID:
        query += f" AND Employee_ID = {Employee_ID}"
    if Approver_ID:
        query += f" AND Approver_ID = {Approver_ID}"
    if Status:
        query += f" AND Status = {Status}"

    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400
    
    values = ()
    
    query, values = apply_date_filters(query, values, start_date, end_date)
    
    if page and page_size:
        offset = (int(page) - 1) * int(page_size)
        query += f" LIMIT {page_size} OFFSET {offset}"

    cursor.execute(query, values)

    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(requests), 200

# ** get all requests by employee id (add filters)
@app.route('/request/employee/<int:Employee_ID>', methods=['GET'])
def get_request_by_employee_id(Employee_ID):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT Request_ID, Employee_ID, Approver_ID, Date, Reason, Status FROM Request WHERE Employee_ID = %s")
    values = (Employee_ID,)

     # ** Extract the parameters from the query string
    Status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if Status:
        query += f" AND Status = {Status}"

    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400
    
    query, values = apply_date_filters(query, values, start_date, end_date)

    # ** pagination parameters
    page = request.args.get('page')
    page_size = request.args.get('page_size')

    if page and page_size:
        offset = (int(page) - 1) * int(page_size)
        query += f" LIMIT {page_size} OFFSET {offset}"

    cursor.execute(query, values)

    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    if not requests:
        return jsonify({'message': 'No requests found'}), 404
    else:
        return jsonify(requests), 200

# ** get all requests by approver id (add filters)
@app.route('/request/approver/<int:Approver_ID>', methods=['GET'])
def get_request_by_approver_id(Approver_ID):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT Request_ID, Employee_ID, Approver_ID, Date, Reason, Status FROM Request WHERE Approver_ID = %s")
    values = (Approver_ID,)

    # ** Extract the parameters from the query string
    Employee_ID = request.args.get('Employee_ID')
    Status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if Employee_ID:
        query += f" AND Employee_ID = {Employee_ID}"
    if Status:
        query += f" AND Status = {Status}"

    if (start_date and not validate_date(start_date)) or (end_date and not validate_date(end_date)):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400
    
    query, values = apply_date_filters(query, values, start_date, end_date)
    

    # ** pagination parameters
    page = request.args.get('page')
    page_size = request.args.get('page_size')

    if page and page_size:
        offset = (int(page) - 1) * int(page_size)
        query += f" LIMIT {page_size} OFFSET {offset}"


    cursor.execute(query, values)

    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    if not requests:
        return jsonify({'message': 'No requests found'}), 404
    else:
        return jsonify(requests), 200

# ** get request by id (add filters)
@app.route('/request/<int:Request_ID>', methods=['GET'])
def get_request_by_id(Request_ID):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT Request_ID, Employee_ID, Approver_ID, Date, Reason, Status FROM Request WHERE Request_ID = %s")
    values = (Request_ID,)

    cursor.execute(query, values)

    request = cursor.fetchone()

    cursor.close()
    conn.close()

    if not request:
        return jsonify({'message': 'Request not found'}), 404
    else:
        return jsonify(request), 200

# ** create a request
@app.route('/request/create', methods=['POST'])
def create_request():
    data  = request.get_json()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    Employee_ID = data['Employee_ID']
    Approver_ID = data['Approver_ID']
    Reason = data['Reason']
    Status = 0
    Date = data['Date']

    # ** validate date format
    if not validate_date(Date):
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    # ** check if the request already exists
    check_exist = check_if_request_exists_by_employee_id_date(Employee_ID, Date)

    if check_exist:
        return jsonify({'message': 'Request already exists'}), 409

    try:
        query = ("INSERT INTO Request (Employee_ID, Approver_ID, Date, Reason, Status) VALUES (%s, %s, %s, %s, %s)")
        values = (Employee_ID, Approver_ID, Date, Reason, Status)
        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Request created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ** update a request status
@app.route('/request/update/<int:Request_ID>', methods=['PUT'])
def update_request(Request_ID):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    Status = request.args.get('Status')

    try:
        query = ("UPDATE Request SET Status = %s WHERE Request_ID = %s")
        values = (Status, Request_ID)

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Request updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ** update a request by id (update date, Reason)
@app.route('/request/update/byuser/<int:Request_ID>', methods=['PUT'])
def update_request_by_user(Request_ID):
    data = request.get_json()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    Date = data['Date']
    Reason = data['Reason']

    # ** validate date format
    if not validate_date(Date):
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    try:
        query = ("UPDATE Request SET Date = %s, Reason = %s WHERE Request_ID = %s")
        values = (Date, Reason, Request_ID)

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Request updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ** delete a request by id
@app.route('/request/delete/<int:Request_ID>', methods=['DELETE'])
def delete_request(Request_ID):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("DELETE FROM Request WHERE Request_ID = %s")
    values = (Request_ID,)

    cursor.execute(query, values)

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Request deleted successfully!'}), 200

# ** check if request exists by employee id and date
def check_if_request_exists_by_employee_id_date(employee_id, date):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT * FROM Request WHERE Employee_ID = %s AND Date = %s")
    values = (employee_id, date)
    cursor.execute(query, values)

    request = cursor.fetchone()

    cursor.close()
    conn.close()

    return request

# ** Utility function to validate date format
def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
# ** Utility function to apply date filters to a query
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5000", debug=True)