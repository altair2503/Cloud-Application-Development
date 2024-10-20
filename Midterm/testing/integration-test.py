import unittest
from flask import json
from main import app
import requests_mock

# Define your secret key
SECRET_KEY = "AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE"

class PhonebookAppIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create a contact with the secret_key header
        response = self.app.post('/contacts', 
                                 json={"name": "Test Name", "phone": "1234567890"},
                                 headers={'secret_key': SECRET_KEY})

        print(response.data)  # Debug print

        # Check if the response is successful
        if response.status_code == 201:  # 201 for created
            self.contact_id = response.get_json()["id"]
        else:
            self.contact_id = None  # Handle the case when the contact isn't created

    @requests_mock.Mocker()
    def test_create_contact_integration(self, mock_requests):
        mock_requests.post('https://inputvalidation-zqyj4gfxea-uc.a.run.app', json={}, status_code=200)
        mock_requests.post('https://logevents-zqyj4gfxea-uc.a.run.app', json={}, status_code=200)
        
        response = self.app.post('/contacts', 
                                 json={"name": "Integration Test Name", "phone": "0987654321"},
                                 headers={'secret_key': SECRET_KEY})
        self.assertEqual(response.status_code, 201)  # 201 for created
        self.assertIn("id", json.loads(response.data))

    @requests_mock.Mocker()
    def test_get_contact_integration(self, mock_requests):
        response = self.app.get(f'/contacts/{self.contact_id}', headers={'secret_key': SECRET_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", json.loads(response.data))

    @requests_mock.Mocker()
    def test_update_contact_integration(self, mock_requests):
        mock_requests.post('https://inputvalidation-zqyj4gfxea-uc.a.run.app', json={}, status_code=200)
        mock_requests.post('https://logevents-zqyj4gfxea-uc.a.run.app', json={}, status_code=200)

        response = self.app.put(f'/contacts/{self.contact_id}', 
                                json={"name": "Updated Test Name", "phone": "1231231234"},
                                headers={'secret_key': SECRET_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", json.loads(response.data))

    @requests_mock.Mocker()
    def test_delete_contact_integration(self, mock_requests):
        mock_requests.post('https://logevents-zqyj4gfxea-uc.a.run.app', json={}, status_code=200)
        response = self.app.delete(f'/contacts/{self.contact_id}', headers={'secret_key': SECRET_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", json.loads(response.data))

if __name__ == '__main__':
    unittest.main()
