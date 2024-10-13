import unittest
import requests

class TestRequestAPI(unittest.TestCase):
    def setUp(self):
        self.API_URL = "http://host.docker.internal:5003"
    
    def test_get_requests(self):
        response = requests.get(self.API_URL + "/request")
        self.assertEqual(response.status_code, 200)
    
    def test_get_requests_by_employee_id(self):
        id = 190052
        response = requests.get(self.API_URL + "/request?Employee_ID={}".format(id))
        self.assertEqual(response.status_code, 200)
    
    def test_get_requests_by_approver_id(self):
        id = 150008
        response = requests.get(self.API_URL + "/request?Approver_ID={}".format(id))
        self.assertEqual(response.status_code, 200)
    
    def test_get_requests_by_status(self):
        status = 1
        response = requests.get(self.API_URL + "/request?Status={}".format(status))
        self.assertEqual(response.status_code, 200)
    
    def test_get_requests_by_start_end_date(self):
        start_date = "2024-09-26"
        end_date = "2024-12-05"
        response = requests.get(self.API_URL + "/request?start_date={}&end_date={}".format(start_date, end_date))
        self.assertEqual(response.status_code, 200)

    def test_get_request_by_employee_id(self):
        id = 210026
        response = requests.get(self.API_URL + "/request/employee/{}".format(id))
        self.assertEqual(response.status_code, 200)
        # expected_response = [
        #     {
        #         "Approver_ID": 210001,
        #         "Date": "Sat, 23 Nov 2024 00:00:00 GMT",
        #         "Employee_ID": 210026,
        #         "Reason": "WFH on November 23th",
        #         "Request_ID": 4,
        #         "Status": 0
        #     },
        #     {
        #         "Approver_ID": 210001,
        #         "Date": "Tue, 26 Nov 2024 00:00:00 GMT",
        #         "Employee_ID": 210026,
        #         "Reason": "WFH on November 26th",
        #         "Request_ID": 5,
        #         "Status": 1
        #     },
        #     {
        #         "Approver_ID": 210001,
        #         "Date": "Sun, 08 Dec 2024 00:00:00 GMT",
        #         "Employee_ID": 210026,
        #         "Reason": "WFH on December 8th",
        #         "Request_ID": 6,
        #         "Status": 0
        #     }
        # ]
        # self.assertEqual(response.json(), expected_response)

    def test_get_requests_by_id(self):
        id = 1
        response = requests.get(self.API_URL + "/request/{}".format(id))
        self.assertEqual(response.status_code, 200)
        # expected_response = {
        #     "Approver_ID": 150008,
        #     "Date": "Sat, 30 Nov 2024 00:00:00 GMT",
        #     "Employee_ID": 190052,
        #     "Reason": "WFH on November 30th",
        #     "Request_ID": 1,
        #     "Status": 1
        # }
        # self.assertEqual(response.json(), expected_response)

    def test_create_request(self):
        obj = {
            "Employee_ID": 190052,
            "Approver_ID": 150008,
            "Date": "2024-11-09",
            "Reason": "WFH on December 12th",
            "Status": 0
        }
        response = requests.post(self.API_URL + "/request/create", json = obj)
        if (response.status_code == 201):
            expected_response = {
                "message": "Request created successfully!"
            }
        elif (response.status_code == 409):
            expected_response = {
                "message": "Request already exists"
            }

        self.assertEqual(response.json(), expected_response)

    def test_update_request(self):
        id = len(requests.get(self.API_URL + "/request").json()) - 1

        status = 1
        response = requests.put(self.API_URL + "/request/update/{}?Status={}".format(id, status))
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "message": "Request updated successfully!"
        }
        self.assertEqual(response.json(), expected_response)

    def test_update_request_by_user(self):
        id = len(requests.get(self.API_URL + "/request").json()) - 1

        obj = {
            "Date": "2024-11-29",
            "Reason": "Update Request - WFH on November 29th"
        }
        response = requests.put(self.API_URL + "/request/update/byuser/{}".format(id), json = obj)
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "message": "Request updated successfully!"
        }
        self.assertEqual(response.json(), expected_response)


    def test_delete_request(self):
        id = len(requests.get(self.API_URL + "/request").json()) - 1

        response = requests.delete(self.API_URL + "/request/delete/{}".format(id))
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
