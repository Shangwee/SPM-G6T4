import unittest
import flask_testing
import requests
from flexible_arrangement import create_app

REQUEST_SERVICE_URL = "http://host.docker.internal:5003"
SCHEDULE_SERVICE_URL = "http://host.docker.internal:5002"

request_id = 0

class TestFlexibleArrangementAPI(flask_testing.TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    # ** get own arrangement
    def test_get_own_arrangement(self):
        response = self.client.get('/flexibleArrangement/ownRequests/151547')
        self.assertEqual(response.status_code, 200)

    def test_get_own_arrangement_not_exist(self):
        response = self.client.get('/flexibleArrangement/ownRequests/1223455')
        self.assertEqual(response.status_code, 404)

    # ** get request for approval
    def test_get_request_for_approval(self):
        response = self.client.get('/flexibleArrangement/approvalRequests/140894')
        self.assertEqual(response.status_code, 200)

    def test_get_request_for_approval_not_exist(self):
        response = self.client.get('/flexibleArrangement/requestForApproval/1223455')
        self.assertEqual(response.status_code, 404)

    # ** create a request
    def test_create_request(self):
        response = self.client.post('/flexibleArrangement/createRequest', json={"staff_id": 151547, "date": "2024-12-05", "reason": "WFH on December 5th"})
        self.assertEqual(response.status_code, 201)

    def test_create_request_invalid_date(self):
        response = self.client.post('/flexibleArrangement/createRequest', json={"staff_id": 151547, "date": "2024-10-05", "reason": "WFH on october 10th"})
        self.assertEqual(response.status_code, 400)

    def test_create_request_already_exists(self):
        response = self.client.post('/flexibleArrangement/createRequest', json={"staff_id": 151547, "date": "2024-12-05", "reason": "WFH on December 5th"})
        self.assertEqual(response.status_code, 409)

    def test_create_request_invalid_staff_id(self):
        response = self.client.post('/flexibleArrangement/createRequest', json={"staff_id": 1223455, "date": "2024-12-05", "reason": "WFH on December 12th"})
        self.assertEqual(response.status_code, 400)

    # ** update a request
    def test_update_request(self):
        response = self.client.put('/flexibleArrangement/updateRequest', json={"staff_id":170866, "request_id": 8, "date": "2024-12-13", "reason": "WFH on December 13th"})
        self.assertEqual(response.status_code, 200)

    def test_update_request_invalid_date(self):
        response = self.client.put('/flexibleArrangement/updateRequest', json={"staff_id": 171009, "request_id": 8, "date": "2024-10-05", "reason": "WFH on october 5th"})
        self.assertEqual(response.status_code, 400)
    
    def test_update_request_not_pending(self):
        response = self.client.put('/flexibleArrangement/updateRequest', json={"staff_id": 171009, "request_id": 9, "date": "2024-12-13", "reason": "WFH on December 13th"})
        self.assertEqual(response.status_code, 400)

    def test_update_request_not_exist(self):
        response = self.client.put('/flexibleArrangement/updateRequest', json={"staff_id": 151547, "request_id": 1223455, "date": "2024-12-13", "reason": "WFH on December 13th"})
        self.assertEqual(response.status_code, 404)

    def test_update_request_wrong_staff_id(self):
        response = self.client.put('/flexibleArrangement/updateRequest', json={"staff_id": 210001, "request_id": 8, "date": "2024-12-13", "reason": "WFH on December 13th"})
        self.assertEqual(response.status_code, 401)

    # ** withdraw a request
    def test_withdraw_wrong_staff_id(self):
        response = self.client.delete('/flexibleArrangement/withdrawRequest', json={"staff_id":  210026, "request_id": 3})
        self.assertEqual(response.status_code, 401)

    def test_withdraw_date_passed(self):
        response = self.client.delete('/flexibleArrangement/withdrawRequest', json={"staff_id": 140002, "request_id": 14})
        self.assertEqual(response.status_code, 400)

    def test_withdraw_request_not_pending(self):
        response = self.client.delete('/flexibleArrangement/withdrawRequest', json={"staff_id": 140002, "request_id": 14})
        self.assertEqual(response.status_code, 400)
    
    def test_withdraw_request_not_exist(self):
        response = self.client.delete('/flexibleArrangement/withdrawRequest', json={"staff_id": 151547, "request_id": 1223455})
        self.assertEqual(response.status_code, 404)

    def test_withdraw_request(self):
        response = self.client.delete('/flexibleArrangement/withdrawRequest', json={"staff_id": 151547, "request_id": 18})
        self.assertEqual(response.status_code, 200)