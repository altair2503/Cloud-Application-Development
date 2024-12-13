from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
import datetime, re, jwt, uuid, requests
from google.cloud import pubsub_v1

# Initialize Flask app
app = Flask(__name__)

# Pub/Sub Configuration
PUBSUB_TOPIC = "projects/cloud-dev-final-ak/topics/post-events"  
publisher = pubsub_v1.PublisherClient()

# Cloud Functions 
INPUT_VALIDATION_URL = "https://us-central1-cloud-dev-final-ak.cloudfunctions.net/inputValidation"
EVENT_NOTIFICATION_URL = ""

# Firebase configuration
FIREBASE_WEB_API_KEY = 'AIzaSyB_Q-XK6V0_gdtQBPkaFaDEEYmZLGTKbZE'
cred = credentials.Certificate("serivce-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Utility function to get Firebase REST API endpoints
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts"

def generate_jwt(uid):
    # Using firebase-admin's create_custom_token to generate JWT
    token = firebase_admin.auth.create_custom_token(uid)
    return token.decode('utf-8')


# Helper to extract userID from JWT
def extract_user_id_from_jwt():
    try:
        token = request.headers.get("Authorization").split(" ")[1]  # Bearer <token>
        decoded_token = jwt.decode(token, options={"verify_signature": False})  # Don't verify the signature for decoding
        print(decoded_token)
        return decoded_token.get("uid")
    except Exception:
        return None


# Function to validate the request using the Cloud Function
def validate_request(post_data):
    try:
        response = requests.post(
            INPUT_VALIDATION_URL,
            json=post_data,
            headers={'Content-Type': 'application/json'}
        )
        # Return the JSON response and status code
        return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': 'Failed to connect to validation service'}, 500


def log_event(post_data, method):
    try:
        message = {
            "title": post_data.get('tittle'),
            "text": post_data.get('text'),
            "category": post_data.get('category'),
            "method": method
        }

        # Publish message to Pub/Sub topic
        future = publisher.publish(PUBSUB_TOPIC, data=str(message).encode("utf-8"))
        print(f"Published message to Pub/Sub: {message}, Message ID: {future.result()}")
    except Exception as e:
        print(f"Failed to publish message to Pub/Sub: {e}")


# Sign-up Endpoint
@app.route('/signup', methods=['POST'])
def sign_up():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        # Request to Firebase Authentication
        url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_WEB_API_KEY}"
        response = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code

        # Create user in Firestore
        user_data = response.json()
        user_id = user_data["localId"]
        db.collection("User").document(user_id).set({
            "id": user_id,
            "name": name,
            "favoriteCategories": []
        })

        return jsonify({"message": "User signed up successfully!", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        # Request to Firebase Authentication
        url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        response = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code

        # Return JWT token
        user_data = response.json()
        jwt_token = generate_jwt(user_data["localId"])
        return jsonify({"message": "Login successful!", "token": jwt_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# CRUD for Posts
@app.route('/posts', methods=['POST'])
def create_post():
    try:
        data = request.json

        # Validate the request data using the Cloud Function
        validation_result, status_code = validate_request(data)
        if status_code != 200:
            # If validation fails, return the validation error response
            return jsonify(validation_result), status_code

        user_id = extract_user_id_from_jwt()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        post_id = str(uuid.uuid4())
        created_time = datetime.datetime.utcnow()

        post_data = {
            "id": post_id,
            "tittle": data.get("tittle"),
            "text": data.get("text"),
            "category": data.get("category"),
            "userID": user_id,
            "createdTime": created_time
        }

        db.collection("Post").document(post_id).set(post_data)

        # Log the event
        log_event(post_data, "POST")

        return jsonify({"message": "Post created successfully!", "post": post_data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/posts', methods=['GET'])
def get_user_posts():
    try:
        user_id = extract_user_id_from_jwt()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        posts_ref = db.collection("Post").where("userID", "==", user_id)
        posts = [post.to_dict() for post in posts_ref.stream()]

        return jsonify({"posts": posts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        user_id = extract_user_id_from_jwt()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.json
        post_ref = db.collection("Post").document(post_id)
        post = post_ref.get()

        if not post.exists:
            return jsonify({"error": "Post not found"}), 404

        post_data = post.to_dict()
        if post_data["userID"] != user_id:
            return jsonify({"error": "Forbidden"}), 403

        post_ref.update(data)
        updated_post = post_ref.get().to_dict()
        return jsonify({"message": "Post updated successfully!", "post": updated_post}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        user_id = extract_user_id_from_jwt()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        post_ref = db.collection("Post").document(post_id)
        post = post_ref.get()

        if not post.exists:
            return jsonify({"error": "Post not found"}), 404

        post_data = post.to_dict()
        if post_data["userID"] != user_id:
            return jsonify({"error": "Forbidden"}), 403

        post_ref.delete()
        return jsonify({"message": "Post deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Search Posts by tittle or text
@app.route('/posts/search', methods=['GET'])
def search_posts():
    try:
        query = request.args.get("query")
        posts_ref = db.collection("Post")
        posts = posts_ref.stream()

        # Use regex to match query in tittle or text
        matching_posts = [
            post.to_dict()
            for post in posts
            if re.search(query, post.to_dict().get("tittle", ""), re.IGNORECASE)
            or re.search(query, post.to_dict().get("text", ""), re.IGNORECASE)
        ]

        return jsonify({"posts": matching_posts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# CRUD for favoriteCategories of User based on JWT
@app.route('/users/favoriteCategories', methods=['GET', 'POST', 'PUT', 'DELETE'])
def favorite_categories():
    user_id = extract_user_id_from_jwt()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user_ref = db.collection("User").document(user_id)
        if not user_ref.get().exists:
            return jsonify({"error": "User not found"}), 404

        if request.method == 'GET':
            # Retrieve favoriteCategories
            user = user_ref.get().to_dict()
            return jsonify({"favoriteCategories": user.get("favoriteCategories", [])}), 200

        elif request.method == 'POST':
            # Add a new category
            category = request.json.get("category")
            user_ref.update({"favoriteCategories": firestore.ArrayUnion([category])})
            return jsonify({"message": f"Category '{category}' added to favoriteCategories!"}), 200

        elif request.method == 'PUT':
            # Replace the entire list of favoriteCategories
            categories = request.json.get("categories", [])
            user_ref.update({"favoriteCategories": categories})
            return jsonify({"message": "favoriteCategories updated!", "categories": categories}), 200

        elif request.method == 'DELETE':
            # Remove a category
            category = request.json.get("category")
            user_ref.update({"favoriteCategories": firestore.ArrayRemove([category])})
            return jsonify({"message": f"Category '{category}' removed from favoriteCategories!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Retrieve posts that are in favoriteCategories of the user based on JWT
@app.route('/users/favoriteCategories/posts', methods=['GET'])
def get_posts_in_favorite_categories():
    user_id = extract_user_id_from_jwt()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user_ref = db.collection("User").document(user_id)
        user = user_ref.get().to_dict()

        if not user:
            return jsonify({"error": "User not found"}), 404

        favorite_categories = user.get("favoriteCategories", [])
        if not favorite_categories:
            return jsonify({"message": "User has no favorite categories.", "posts": []}), 200

        posts_ref = db.collection("Post")
        posts = posts_ref.stream()

        # Filter posts by favoriteCategories
        filtered_posts = [
            post.to_dict()
            for post in posts
            if post.to_dict().get("category") in favorite_categories
        ]

        return jsonify({"posts": filtered_posts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)