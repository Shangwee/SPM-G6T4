from flask import Flask, request,jsonify
import requests
from datetime import datetime
from flask_cors import CORS

# Microservice URL configurations
ACCOUNTS_SERVICE_URL = "http://host.docker.internal:5001"
SCHEDULE_SERVICE_URL = "http://host.docker.internal:5002"
REQUEST_SERVICE_URL = "http://host.docker.internal:5003"

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/manageRequest/reject', methods=['POST'])
    def reject():
        # get the staff_id and request_id from the request body
        data = request.get_json()
        staff_id = data['staff_id']
        request_id = data['request_id']

        # check if the user is allowed to reject the request
        role = check_staff_role(staff_id)
        if role == 1 or role == 3:
            # retrieve the request from the request service
            retrieve_request = requests.get(f"{REQUEST_SERVICE_URL}/request/{request_id}")

            if retrieve_request.status_code == 200:
                retrieve_request = retrieve_request.json()

                approver_id = retrieve_request['Approver_ID']

                # check if status is pending
                status = retrieve_request['Status']

                # check if the user is allowed to reject the request
                if approver_id != staff_id:
                    return jsonify({'error': 'You are not allowed to reject this request'}), 401

                if status == 2:
                    return jsonify({'error': 'Request has been rejected'}), 401
                if status == 1:
                    return jsonify({'error': 'Request has been accepted'}), 401

                # reject the request
                update_status = requests.put(f"{REQUEST_SERVICE_URL}/request/update/{request_id}?Status=2")
                if update_status.status_code == 200:
                    return jsonify({'message': 'Request rejected successfully'}), 200
                else:
                    return jsonify({'error': 'Failed to reject the request'}), 500
            else:
                return jsonify({'error': 'Failed to retrieve the request'}), 500
        # if the user is not allowed to reject the request
        return jsonify({'error': 'You are not allowed to reject this request'}), 401

    @app.route('/manageRequest/accept', methods=['POST'])
    def accept():
        # get the staff_id and request_id from the request
        data = request.get_json()
        staff_id = data['staff_id']
        request_id = data['request_id']

        # check if the user is allowed to accept the request
        role = check_staff_role(staff_id)
        if role == 1 or role == 3:
            # retrieve the request from the request service
            retrieve_request = requests.get(f"{REQUEST_SERVICE_URL}/request/{request_id}")

            if retrieve_request.status_code == 200:
                retrieve_request = retrieve_request.json()

                approver_id = retrieve_request['Approver_ID']

                # check if the user is allowed to accept the request
                if approver_id != staff_id:
                    return jsonify({'error': 'You are not allowed to accept this request'}), 401

                # check if status is pending
                status = retrieve_request['Status']

                if status == 2:
                    return jsonify({'error': 'Request has been rejected'}), 401
                if status == 1:
                    return jsonify({'error': 'Request has been accepted'}), 401
                
                # accept the request
                update_status = requests.put(f"{REQUEST_SERVICE_URL}/request/update/{request_id}?Status=1")

                if update_status.status_code == 200:
                    # add the request to the schedule
                    add_schedule = add_to_schedule(request_id)
                    if add_schedule.status_code == 201:
                        return jsonify({'message': 'Request accepted and added to schedule'}), 200
                    else:
                        return jsonify({'error': 'Failed to add the request to the schedule'}), 500
            else:
                return jsonify({'error': 'Failed to retrieve the request'}), 500
        # if the user is not allowed to accept the request
        return jsonify({'error': 'You are not allowed to accept this request'}), 401
    
    @app.route('/manageRequest/withdraw', methods=['POST'])
    def withdraw():
        # get the staff_id and request_id from the request
        data = request.get_json()
        staff_id = data['staff_id']
        request_id = data['request_id']

        # check if the user is allowed to accept the request
        role = check_staff_role(staff_id)
        if role == 1 or role == 3:
            # retrieve the request from the request service
            retrieve_request = requests.get(f"{REQUEST_SERVICE_URL}/request/{request_id}")

            if retrieve_request.status_code == 200:
                retrieve_data = retrieve_request.json()
                approver_id = retrieve_data['Approver_ID']
                status = retrieve_data['Status']

                # check if the user is allowed to withdraw the request
                if approver_id == staff_id:
                    if status == 1:
                        # update status to rejected
                        update_status = requests.put(f"{REQUEST_SERVICE_URL}/request/update/{request_id}?Status=2")
                        if update_status.status_code == 200:
                            # delete the request from the schedule
                            delete_schedule = requests.delete(f"{SCHEDULE_SERVICE_URL}/schedule/delete/request/{request_id}")
                            if delete_schedule.status_code == 200:
                                return jsonify({'message': 'Request withdrawn successfully'}), 200
                            else:
                                return jsonify({'error': 'Failed to withdraw the request'}), 500
                        else:
                            return jsonify({'error': 'Failed to withdraw the request'}), 500
                    else:
                        return jsonify({'error': 'You are not allowed to withdraw this request'}), 401
                else:
                    return jsonify({'error': 'You are not allowed to withdraw this request'}), 401
            else:
                return jsonify({'error': 'Failed to retrieve the request'}), 500
        else:
            return jsonify({'error': 'You are not allowed to withdraw this request'}), 401

    def check_staff_role(staff_id):
        Employee = requests.get(f"{ACCOUNTS_SERVICE_URL}/user/{staff_id}")
        if Employee.status_code == 200:
            Employee = Employee.json()
            return Employee['Role']
        return None

    def add_to_schedule(request_id):
        # retrieve the request from the request service
        retrieve_request = requests.get(f"{REQUEST_SERVICE_URL}/request/{request_id}")
        if retrieve_request.status_code == 200:
            retrieve_request = retrieve_request.json()
            date = retrieve_request['Date']
            employee_id = retrieve_request['Employee_ID']

            ## format the date as yyyy-mm-dd
            date_object = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
            formatted_date = date_object.strftime('%Y-%m-%d')

            # add the request to the schedule
            add_to_schedule = requests.post(f"{SCHEDULE_SERVICE_URL}/schedule", json={'staff_id': employee_id, 'date': formatted_date, 'request_id': request_id})

            return add_to_schedule
        # if the request does not exist
        return jsonify({'error': 'Failed to retrieve the request'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=6002, debug=True)