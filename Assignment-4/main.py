from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory phonebook and ID counter
phonebook = {}
next_contact_id = 1  # Start with ID 1

# Health Check Endpoints

# Liveness check endpoint
@app.route('/health', methods=['GET'])
def healthz():
    # Just returns a 200 OK if the app is alive
    return jsonify({"status": "ok"}), 200

# Readiness check endpoint
@app.route('/readiness', methods=['GET'])
def readiness():
    # Check if phonebook is empty, which might be a simple readiness check (or use other logic)
    if len(phonebook) >= 0:  # You could make this check more complex if needed
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "not ready"}), 503

# Create a new contact
@app.route('/contacts', methods=['POST'])
def create_contact():
    global next_contact_id
    contact_data = request.json

    # Proceed to create the contact if validation succeeds
    contact = {
        'id': next_contact_id,
        'name': contact_data['name'],
        'phone': contact_data['phone']
    }
    phonebook[next_contact_id] = contact
    next_contact_id += 1  # Increment the ID for the next contact

    return jsonify(contact), 201

# Read all contacts
@app.route('/contacts', methods=['GET'])
def get_contacts():
    return jsonify(list(phonebook.values())), 200

# Read a specific contact by ID
@app.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = phonebook.get(contact_id)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404
    return jsonify(contact), 200

# Update a contact
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    contact = phonebook.get(contact_id)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404
    updated_data = request.json
    contact['name'] = updated_data.get('name', contact['name'])
    contact['phone'] = updated_data.get('phone', contact['phone'])

    return jsonify(contact), 200

# Delete a contact
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = phonebook.pop(contact_id, None)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404

    return jsonify({'message': 'Contact deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)