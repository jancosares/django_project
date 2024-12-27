# django_project
Support Central

System Overview

Support Central is a customer support system designed to facilitate seamless communication between customers and administrators through a secure messaging platform. This system provides end-to-end encrypted communication, ensuring confidentiality and data integrity. Built with Django REST Framework, Support Central features user authentication, message encryption, and an intuitive dashboard for managing users and messages.

Features

1. User Authentication

Secure login and registration system with token-based session management.

Ensures user privacy and access control.

2. Messaging System

Secure APIs for sending and receiving messages.

Messages are encrypted before transmission and decrypted upon receipt using custom middleware.

3. Encryption and Security

Middleware for encryption, hashing, and request validation.

Guarantees safe and tamper-proof data transmission.

4. Admin Dashboard

Intuitive interface to manage users and messages.

Overview of all system activities in a single, user-friendly display.

5. Responsive Interface

Visually appealing design with a responsive layout for seamless user experience.

6. Customer Support Features

Customers can seek assistance by sending messages directly to the admin.

Real-time responses from admins help resolve issues efficiently.

User-friendly chat interface for customers to initiate and track support queries.

Technical Stack and Tools

Backend

Django 5.0+

Django Channels

PostgreSQL

Frontend

Bootstrap

CSS

JavaScript

Development Tools

Git/GitHub

VS Code / IntelliJ IDEA 2024.2.2

Installation and Setup

Step 1: Clone the Repository

https://github.com/jancosares/django_project.git

Step 2: Install Python

Ensure Python is installed on your system. You can download it from Python.org.

Step 3: Set Up a Virtual Environment

python -m venv venv
venv/Scripts/activate

Step 4: Install Required Packages

pip install environ
pip install django-environ
pip install Django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install psycopg
pip install cryptography

Step 5: Navigate to the Project Directory

cd django_project

Step 6: Configure the Database

Edit the settings.py file in the project directory to configure your PostgreSQL database.

Step 7: Generate a FERNET Key for Encryption

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Add this key to the project settings for encryption.

Step 8: Run Migrations

python manage.py migrate

Step 9: Start the Development Servers

Run the servers for both the admin and user applications:

admin: python manage.py runserver 8000
user: python manage.py runserver 8001 - Depends on the user what port number should use

Security Considerations

Ensure the FERNET_KEY is stored securely and not hard-coded in the repository.

Use HTTPS for all communications in production.

Contributing

Contributions are welcome! Please follow these steps:

Fork the repository.

Create a new branch (feature/your-feature-name).

Commit your changes.

Open a pull request.

Middleware Features

Message Encryption and Decryption

Secures outgoing message payloads with Fernet encryption.

Ensures all transmitted data is safe and tamper-proof.

Decodes incoming encrypted messages.

Verifies message integrity and ensures authorized access.

Middleware Implementation:

from django.utils.deprecation import MiddlewareMixin
from cryptography.fernet import Fernet
from django.conf import settings
from .models import Message

# Retrieve the Fernet key from settings
FERNET_KEY = settings.FERNET_KEY
cipher_suite = Fernet(FERNET_KEY)

class EncryptionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = False  # Django 5.x compatibility

    def __call__(self, request):
        # Handle request decryption before it reaches the view
        self.decrypt_request(request)
        
        # Process the request and get the response
        response = self.get_response(request)
        
        # Handle response encryption before it is returned
        self.encrypt_response(response)

        return response

    def decrypt_request(self, request):
        """Decrypt message content in the request body."""
        if request.method in ['POST', 'PUT', 'PATCH'] and request.body:
            try:
                # Assuming the content is JSON encoded
                decrypted_data = cipher_suite.decrypt(request.body).decode('utf-8')
                request._body = decrypted_data  # Modify the request body with decrypted data
            except Exception as e:
                print(f"Error decrypting request body: {e}")

    def encrypt_response(self, response):
        """Encrypt message content in the response."""
        if response.content and response['Content-Type'] == 'application/json':
            try:
                encrypted_data = cipher_suite.encrypt(response.content)
                response.content = encrypted_data  # Modify the response content with encrypted data
            except Exception as e:
                print(f"Error encrypting response body: {e}")

The models.py file handles user authentication and secure message storage in Support Central. It defines a custom user model for unique email-based login and a Message model that encrypts and decrypts messages to ensure secure communication between users.

Support Central Flow
User Login/Registration

A user registers or logs in using a secure authentication system.
Upon successful authentication, the user gains access to the messaging interface.
User Initiates a Message

The user types a message in the chat interface and sends it.
The message is encrypted using Fernet encryption before being stored in the database.
Message Saved to Database

The encrypted message is stored in the Message table in the PostgreSQL database, along with metadata like sender, receiver, and timestamp.
Admin Views Incoming Messages

The admin logs into their dashboard to view all messages sent by users.
Messages are decrypted in real-time using the FERNET_KEY.
Admin Responds to User

The admin types a response to a selected user message and sends it back.
The response undergoes encryption before being saved in the database.
The user sees the admin's response in their chat interface upon retrieval, where it is decrypted for display.
Admin Manages Users

Response: The admin can directly communicate with users to resolve queries or provide assistance.
Delete Users:
If a user violates terms or is inactive, the admin can delete the user's account.
Upon deletion, the user’s data (messages and account details) is removed from the system.

Admin Manages Messages

The admin can choose to show or hide message logs in the dashboard:
Show Logs: Displays all user messages with decrypted content and metadata (e.g., sender, receiver, timestamp).
Hide Logs: Temporarily hides the messages from view, offering a cleaner interface or restricted access mode.

History and Management

Both users and admins can view the message history, which is securely stored and decrypted only when accessed.
