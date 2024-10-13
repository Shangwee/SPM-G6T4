from flask import Flask, request,jsonify
import requests
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Microservice URL configurations
ACCOUNTS_SERVICE_URL = "http://host.docker.internal:5001"
SCHEDULE_SERVICE_URL = "http://host.docker.internal:5002"
REQUEST_SERVICE_URL = "http://host.docker.internal:5003"

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # ** create request for flexible arrangement
    @app.route('/flexibleArrangement/createRequest', methods=['POST'])
    def create_request():
        # retrieve staff_id, Date and reason from the request body
        data = request.get_json()
        staff_id = data['staff_id']
        date = data['date']
        Reason = data['reason']

        # validate the date
        if not validate_minimum_date(date):
            return jsonify({'error': 'Invalid date. Please select a date at least 24 hours from now'}), 400

        # retrieve Reporting Manager ID from the accounts service
        staff_info = requests.get(f"{ACCOUNTS_SERVICE_URL}/user/{staff_id}")
        if staff_info.status_code == 200:
            staff_info_data = staff_info.json()
            reporting_manager = staff_info_data['Reporting_Manager']

            # create the request
            create_request = requests.post(f"{REQUEST_SERVICE_URL}/request/create", json={
                'Employee_ID': staff_id,
                'Approver_ID': reporting_manager,
                'Date': date,
                'Reason': Reason,
                'Status': 0
            })

            if create_request.status_code == 201:
                data = create_request.json()
                return jsonify(data), 201
            elif create_request.status_code == 409:
                return jsonify({'error': 'Request already exists'}), 409
            else:
                return jsonify({'error': 'Failed to create request'}), 500
        else:
            return jsonify({'error': 'Failed to retrieve staff information'}), 400

    # ** update request for flexible arrangement
    @app.route('/flexibleArrangement/updateRequest', methods=['PUT'])
    def update_request():
        # retrieve staff_id, request_id, date and reason from the request body
        data = request.get_json()
        staff_id = data['staff_id']
        request_id = data['request_id']
        date = data['date']
        Reason = data['reason']

        # validate the date
        if not validate_minimum_date(date):
            return jsonify({'error': 'Invalid date. Please select a date at least 24 hours from now'}), 400
        
        # retrieve request from the request service
        retrieve_request = requests.get(f"{REQUEST_SERVICE_URL}/request/{request_id}")

        if retrieve_request.status_code == 200:
            retrieve_request_data = retrieve_request.json()
            Date = retrieve_request_data['Date']
            retrieve_staff_id = retrieve_request_data['Employee_ID']

            # check if the request is pending
            if retrieve_request_data['Status'] == 0:

                # check if the staff_id matches the staff_id in the request
                if staff_id != retrieve_staff_id:
                    return jsonify({'error': 'You are not allowed to update this request'}), 401
                
                ## format the date as yyyy-mm-dd
                date_object = datetime.strptime(Date, '%a, %d %b %Y %H:%M:%S %Z')
                previous_date = date_object.strftime('%Y-%m-%d')

                # update reason with the new reason with  "Updated from {Previous_Date}: " prefix
                new_reason = f"Updated from {previous_date}: {Reason}"
                
                # update the request
                update_request = requests.put(f"{REQUEST_SERVICE_URL}/request/update/byuser/{request_id}", json={
                    'Date': date,
                    'Reason': new_reason
                })

                if update_request.status_code == 200:
                    return jsonify({'message': 'Request updated successfully'}), 200
            else:
                return jsonify({'error': 'Request is not pending, need to create a new request'}), 400
        else:
            return jsonify({'error': 'Failed to retrieve request'}), 404

    # ** withdraw request for flexible arrangement
    @app.route('/flexibleArrangement/withdrawRequest', methods=['DELETE'])
    def withdraw_request():
        # retrieve staff_id and request_id from the request body
        data = request.get_json()
        staff_id = data['staff_id']
        request_id = data['request_id']

        # retrieve request from the request service
        retrieve_request = requests.get(f"{REQUEST_SERVICE_URL}/request/{request_id}")

        # check if date has passed from current date
        if retrieve_request.status_code == 200:
            retrieve_request_data = retrieve_request.json()
            Date = retrieve_request_data['Date']
            status = retrieve_request_data['Status']
            retrieve_staff_id = retrieve_request_data['Employee_ID']

            ## format the date as yyyy-mm-dd
            date_object = datetime.strptime(Date, '%a, %d %b %Y %H:%M:%S %Z')
            formatted_date = date_object.strftime('%Y-%m-%d')

            now = datetime.now()
            if formatted_date < now.strftime('%Y-%m-%d'):
                return jsonify({'error': 'Cannot withdraw request, date has passed'}), 400
            
            # check if the staff_id matches the staff_id in the request
            if staff_id != retrieve_staff_id:
                return jsonify({'error': 'You are not allowed to withdraw this request'}), 401
            
            # check if the request is pending
            if status == 0:
                # withdraw the request
                withdraw_request = requests.delete(f"{REQUEST_SERVICE_URL}/request/delete/{request_id}")

                if withdraw_request.status_code == 200:
                    return jsonify({'message': 'Request withdrawn successfully'}), 200
            else:
                return jsonify({'error': 'Request is not pending, cannot be withdrawn'}), 400
        else:
            return jsonify({'error': 'Failed to retrieve request'}), 404

    # ** retrieve own requests
    @app.route('/flexibleArrangement/ownRequests/<int:staff_id>', methods=['GET'])
    def own_requests(staff_id):
        # extract from query parameters
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # pagination parameters
        page = request.args.get('page')
        page_size = request.args.get('page_size')

        # retrieve own requests
        query_params = []
        if status:
            query_params.append(f"status={status}")
        if page and page_size:
            query_params.append(f"page={page}&page_size={page_size}")
        if start_date:
            query_params.append(f"start_date={start_date}")
        if end_date:
            query_params.append(f"end_date={end_date}")

        query_string = f"/request/employee/{staff_id}"
        if query_params:
            query_string += "?" + "&".join(query_params)

        retrieve_requests = requests.get(f"{REQUEST_SERVICE_URL}{query_string}")

        if retrieve_requests.status_code == 200:
            return jsonify(retrieve_requests.json()), 200
        else:
            return jsonify({'error': 'Failed to retrieve requests'}), 404

    # ** retrieve requests for approval
    @app.route('/flexibleArrangement/approvalRequests/<int:staff_id>', methods=['GET'])
    def approval_requests(staff_id):
        # extract from query parameters
        Employee_ID = request.args.get('Employee_ID')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # pagination parameters
        page = request.args.get('page')
        page_size = request.args.get('page_size')

        # retrieve approval requests
        query_params = []
        if Employee_ID:
            query_params.append(f"Employee_ID={Employee_ID}")
        if status:
            query_params.append(f"status={status}")
        if page and page_size:
            query_params.append(f"page={page}&page_size={page_size}")
        if start_date:
            query_params.append(f"start_date={start_date}")
        if end_date:
            query_params.append(f"end_date={end_date}")

        query_string = f"/request/approver/{staff_id}"
        if query_params:
            query_string += "?" + "&".join(query_params)

        retrieve_requests = requests.get(f"{REQUEST_SERVICE_URL}{query_string}")

        if retrieve_requests is not None:
            # combine the request with the employee information
            requests_data = retrieve_requests.json()
            for request_data in requests_data:
                employee_id = request_data['Employee_ID']
                employee = requests.get(f"{ACCOUNTS_SERVICE_URL}/user/{employee_id}")
                if employee.status_code == 200:
                    employee_data = employee.json()
                    request_data['Staff_FName'] = employee_data['Staff_FName']
                    request_data['Staff_LName'] = employee_data['Staff_LName']
                    request_data['Dept'] = employee_data['Dept']
                    request_data['Email'] = employee_data['Email']
                    request_data['Position'] = employee_data['Position']
                    request_data['Country'] = employee_data['Country']
                    request_data['Role'] = employee_data['Role']
            return jsonify(requests_data), 200
        else:
            return jsonify({'error': 'Failed to retrieve requests'}), 404

    # ** validate the date minimum 24 hr from now
    def validate_minimum_date(date):
        date = datetime.strptime(date, '%Y-%m-%d')
        now = datetime.now()
        if date < now:
            return False
        return True

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=6001, debug=True)