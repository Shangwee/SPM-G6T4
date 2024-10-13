import unittest
import flask_testing
import requests
from manage_request import create_app

REQUEST_SERVICE_URL = "http://host.docker.internal:5003"
SCHEDULE_SERVICE_URL = "http://host.docker.internal:5002"


class TestManageRequestAPI(flask_testing.TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    # ** reject
    def test_reject_request_not_allowed_when_not_approver(self):
        response = self.client.post('/manageRequest/reject', json={"staff_id": 210001, "request_id": 1})
        self.assertEqual(response.status_code, 401)

    def test_reject_request(self):
        response = self.client.post('/manageRequest/reject', json={"staff_id": 150008, "request_id": 1})
        self.assertEqual(response.status_code, 200)

    def test_reject_request_not_allowed_when_rejected_already(self):
        response = self.client.post('/manageRequest/reject', json={"staff_id": 150008, "request_id": 2})
        self.assertEqual(response.status_code, 401)

    def test_reject_request_not_allowed_when_accepted_already(self):
        response = self.client.post('/manageRequest/reject', json={"staff_id": 210001, "request_id": 5})
        self.assertEqual(response.status_code, 401)

    def test_reject_request_not_allowed_when_request_not_exist(self):
        response = self.client.post('/manageRequest/reject', json={"staff_id": 150008, "request_id": 1022211220})
        self.assertEqual(response.status_code, 500)
    
    def test_reject_request_not_allowed_when_not_allowed(self):
        response = self.client.post('/manageRequest/reject', json={"staff_id": 190097, "request_id": 3})
        self.assertEqual(response.status_code, 401)

    # ** accept
    def test_accept_request_not_allowed_when_not_approver(self):
        response = self.client.post('/manageRequest/accept', json={"staff_id": 150008, "request_id": 4})
        self.assertEqual(response.status_code, 401)

    # def test_accept_request(self):
    #     response = self.client.post('/manageRequest/accept', json={"staff_id": 210001, "request_id": 4})
    #     self.assertEqual(response.status_code, 200)

    def test_accept_request_not_allowed_when_accepted_already(self):
        response = self.client.post('/manageRequest/accept', json={"staff_id": 210001, "request_id": 5})
        self.assertEqual(response.status_code, 401)

    def test_accept_request_not_allowed_when_rejected_already(self):
        response = self.client.post('/manageRequest/accept', json={"staff_id": 150008, "request_id": 2})
        self.assertEqual(response.status_code, 401)

    def test_accept_request_not_allowed_when_request_not_exist(self):
        response = self.client.post('/manageRequest/accept', json={"staff_id": 210001, "request_id": 1022211220})
        self.assertEqual(response.status_code, 500)

    def test_accept_request_not_allowed_when_not_allowed(self):
        response = self.client.post('/manageRequest/accept', json={"staff_id": 190097, "request_id": 6})
        self.assertEqual(response.status_code, 401)

    def tearDown(self):
        requests.put(f"{REQUEST_SERVICE_URL}/request/update/1?Status=0")
        requests.put(f"{REQUEST_SERVICE_URL}/request/update/2?Status=2")
        requests.put(f"{REQUEST_SERVICE_URL}/request/update/3?Status=0")
        requests.put(f"{REQUEST_SERVICE_URL}/request/update/4?Status=0")
        requests.put(f"{REQUEST_SERVICE_URL}/request/update/5?Status=1")
        requests.put(f"{REQUEST_SERVICE_URL}/request/update/6?Status=0")

        # reset schedules by getting schedule with request_id 4


if __name__ == '__main__':
    unittest.main()
    

