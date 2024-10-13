import unittest
import flask_testing
from  account import create_app

class TestAccountAPI(flask_testing.TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_get_users(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)

    def test_get_users_by_department(self):
        response = self.client.get('/users?dept=Sales')
        self.assertEqual(response.status_code, 200)

    def test_get_users_by_position(self):
        response = self.client.get('/users?position=Account Manager')
        self.assertEqual(response.status_code, 200)

    def test_get_users_by_country(self):
        response = self.client.get('/users?country=Singapore')
        self.assertEqual(response.status_code, 200)

    def test_get_users_by_role(self):
        response = self.client.get('/users?role=1')
        self.assertEqual(response.status_code, 200)

    def test_get_users_by_reporting_manager(self):
        response = self.client.get('/users?Reporting_Manager=140894')
        self.assertEqual(response.status_code, 200)

    def test_get_users_paginated(self):
        response = self.client.get('/users?page=1&page_size=2')
        self.assertEqual(response.status_code, 200)

    def test_get_user(self):
        response = self.client.get('/user/171009')
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "Country": "Singapore",
            "Dept": "Finance",
            "Email": "Seng.Kesavan@allinone.com.sg",
            "Position": "Finance Manager",
            "Reporting_Manager": 170166,
            "Role": 3,
            "Staff_FName": "Seng",
            "Staff_ID": 171009,
            "Staff_LName": "Kesavan"
        }
        self.assertEqual(response.json, expected_response)

    def test_get_users_batch(self):
        response = self.client.get('/users/batch', json={"staff_ids": [140002, 140008, 140003]})
        self.assertEqual(response.status_code, 200)
        expected_response = [
            {
            "Country": "Singapore",
            "Dept": "Sales",
            "Email": "Susan.Goh@allinone.com.sg",
            "Position": "Account Manager",
            "Reporting_Manager": 140894,
            "Role": 2,
            "Staff_FName": "Susan",
            "Staff_ID": 140002,
            "Staff_LName": "Goh"
            },
            {
            "Country": "Singapore",
            "Dept": "Sales",
            "Email": "Janice.Chan@allinone.com.sg",
            "Position": "Account Manager",
            "Reporting_Manager": 140894,
            "Role": 2,
            "Staff_FName": "Janice",
            "Staff_ID": 140003,
            "Staff_LName": "Chan"
            },
            {
            "Country": "Singapore",
            "Dept": "Sales",
            "Email": "Jaclyn.Lee@allinone.com.sg",
            "Position": "Sales Manager",
            "Reporting_Manager": 140001,
            "Role": 3,
            "Staff_FName": "Jaclyn",
            "Staff_ID": 140008,
            "Staff_LName": "Lee"
            }
        ]
        self.assertEqual(response.json, expected_response)

    def test_login(self):
        response = self.client.post('/login', json={"staffID": 140001, "password": "2ZvBYts7"})
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "Country": "Singapore",
            "Dept": "Sales",
            "Email": "Derek.Tan@allinone.com.sg",
            "Position": "Director",
            "Reporting_Manager": 130002,
            "Role": 1,
            "Staff_FName": "Derek",
            "Staff_ID": 140001,
            "Staff_LName": "Tan"
        }
        self.assertEqual(response.json, expected_response)

    def test_get_departments(self):
        response = self.client.get('/departments')
        self.assertEqual(response.status_code, 200)
        expected_departments = [
            ["CEO"],
            ["Sales"],
            ["Solutioning"],
            ["Engineering"],
            ["HR"],
            ["Finance"],
            ["Consultancy"],
            ["IT"]
        ]
        self.assertEqual(response.json, expected_departments)

if __name__ == '__main__':
    unittest.main()