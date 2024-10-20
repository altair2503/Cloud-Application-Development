from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# In-memory phonebook and ID counter
phonebook = {}
next_contact_id = 1  # Start with ID 1

# Security key
API_KEY = "AIzaSyAV8oQPuVDrC44gW9fOtSXZEYEW7JmVwLE"

# URL for the Cloud Function (replace with your actual Cloud Function URL)
CLOUD_INPUT_VALIDATION = 'https://inputvalidation-zqyj4gfxea-uc.a.run.app'
CLOUD_FUNCTION_LOGGING_URL = 'https://logevents-zqyj4gfxea-uc.a.run.app' 

# Secret key check
def check_secret_key(func):
    def wrapper(*args, **kwargs):
        secret_key = request.headers.get('secret_key')
        if secret_key != API_KEY:
            return jsonify({"error": "Unauthorized: Invalid API Key"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# Function to validate the request using the Cloud Function
def validate_request(contact_data):
    try:
        response = requests.post(
            CLOUD_INPUT_VALIDATION,
            json=contact_data,
            headers={'Content-Type': 'application/json'}
        )
        # Return the JSON response and status code
        return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': 'Failed to connect to validation service'}, 500

# Function to log events using the Cloud Function
def log_event(contact_data, method):
    try:
        response = requests.post(
            CLOUD_FUNCTION_LOGGING_URL,
            json={
                'name': contact_data.get('name'),
                'phone': contact_data.get('phone'),
                'method': method  # Include the HTTP method to indicate the action
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print(f"Failed to log {method} action.")
        else:
            print(f"{method} action logged successfully.")
    except requests.RequestException:
        print("Failed to connect to logging service.")

# Create a new contact
@app.route('/contacts', methods=['POST'])
@check_secret_key
def create_contact():
    global next_contact_id
    contact_data = request.json

    # Validate the request data using the Cloud Function
    validation_result, status_code = validate_request(contact_data)
    if status_code != 200:
        # If validation fails, return the validation error response
        return jsonify(validation_result), status_code

    # Proceed to create the contact if validation succeeds
    contact = {
        'id': next_contact_id,
        'name': contact_data['name'],
        'phone': contact_data['phone']
    }
    phonebook[next_contact_id] = contact
    next_contact_id += 1  # Increment the ID for the next contact

    # Log the creation event
    log_event(contact_data, 'POST')

    return jsonify(contact), 201

# Read all contacts
@app.route('/contacts', methods=['GET'])
@check_secret_key
def get_contacts():
    return jsonify(list(phonebook.values())), 200

# Read a specific contact by ID
@app.route('/contacts/<int:contact_id>', methods=['GET'])
@check_secret_key
def get_contact(contact_id):
    contact = phonebook.get(contact_id)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404
    return jsonify(contact), 200

# Update a contact
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
@check_secret_key
def update_contact(contact_id):
    contact = phonebook.get(contact_id)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404
    updated_data = request.json
    contact['name'] = updated_data.get('name', contact['name'])
    contact['phone'] = updated_data.get('phone', contact['phone'])

    # Log the creation event
    log_event(updated_data, 'PUT')

    return jsonify(contact), 200

# Delete a contact
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
@check_secret_key
def delete_contact(contact_id):
    contact = phonebook.pop(contact_id, None)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404

     # Log the creation event
    log_event(contact, 'DELETE')

    return jsonify({'message': 'Contact deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
