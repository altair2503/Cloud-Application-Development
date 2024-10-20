import unittest
from flask import json
from main import app, phonebook  # Import the Flask app and the phonebook dictionary

class PhonebookAppUnitTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Create a contact to use in tests
        self.contact_data = {"name": "Test User", "phone": "1234567890"}
        response = self.app.post('/contacts', json=self.contact_data, headers={'secret_key': 'AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE'})
        self.contact_id = response.get_json()["id"]

    def test_create_contact(self):
        contact_data = {"name": "New User", "phone": "0987654321"}
        response = self.app.post('/contacts', json=contact_data, headers={'secret_key': 'AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE'})
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", json.loads(response.data))

    def test_get_all_contacts(self):
        response = self.app.get('/contacts', headers={'secret_key': 'AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(json.loads(response.data)), 0)

    def test_get_contact(self):
        response = self.app.get(f'/contacts/{self.contact_id}', headers={'secret_key': 'AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", json.loads(response.data))

    def test_update_contact(self):
        response = self.app.put(f'/contacts/{self.contact_id}', json={"name": "Updated User"}, headers={'secret_key': 'AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", json.loads(response.data))

    def test_delete_contact(self):
        response = self.app.delete(f'/contacts/{self.contact_id}', headers={'secret_key': 'AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", json.loads(response.data))

if __name__ == '__main__':
    unittest.main()
