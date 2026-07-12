from application import create_app
from application.models import db
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
    
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "5551234567",
            "password": "123"
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")

    def test_create_customer_duplicate_email(self):
        customer_payload = {
            "name": "John Doe",
            "email": "duplicate@email.com",
            "phone": "5551234567",
            "password": "123"
        }
        first_response = self.client.post('/customers/', json=customer_payload)
        second_response = self.client.post('/customers/', json=customer_payload)

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 400)
    
    def test_get_all_customers(self):
        customer_payload = {
            "name": "Jane Doe",
            "email": "jane@email.com",
            "phone": "5559876543",
            "password": "4564"

        }
        post_response = self.client.post('/customers/', json=customer_payload)
        print("POST response:", post_response.status_code, post_response.json)  # DEBUG
        response = self.client.get('/customers/')   
        self.assertEqual(response.status_code, 200)
        self.assertIn("Jane Doe", [customer['name'] for customer in response.json['customers']])
    
    def test_get_single_customer(self):
        customer_payload = {
            "name": "Bob Smith",
            "email": "bob@gmail.com",
            "phone": "5555555555",
            "password": "bob123"
        
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['id'] #extract ID

        # get single customer
        response = self.client.get(f'/customers/{customer_id}')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Bob Smith")
        self.assertEqual(response.json['email'], "bob@gmail.com")

    def test_get_single_customer_not_found(self):
        response = self.client.get('/customers/9999')
        self.assertEqual(response.status_code, 400)

    # Test login
    def test_login(self):
        # Create a customer
        customer_payload = {
            "name": "Jasmine Heights",
            "email": "jazzy@gmail.com",
            "phone": "1234567891",
            "password": "jazz123"
        }
        # Get customer payload
        self.client.post('/customers/', json=customer_payload)

        # Try to login
        login_payload={
            "email": "jazzy@gmail.com",
            "password": "jazz123"
        }
        response = self.client.post('/customers/login', json=login_payload)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_login_missing_fields(self):
        login_payload = {
            "email": "jazzy@gmail.com"
        }
        response = self.client.post('/customers/login', json=login_payload)

        self.assertEqual(response.status_code, 400)

    # Invalid password test
    def test_login_invalid_password(self):
        # create customer
        customer_payload = {
            "name":"Jasmine Heights",
            "email": "jazzy@gmail.com",
            "phone": "1234567891",
            "password": "jazz123"
        }
        self.client.post('/customers/', json=customer_payload)

        # login with wrong password
        login_payload = {
            "email": "jazzy@gmail.com",
            "password": "jazzz123"
        }
        response = self.client.post('/customers/login', json=login_payload)

        # Assert Error
        self.assertEqual(response.status_code, 400)

    # Test customer update
    def test_update_customer(self):
        customer_payload = {
            "name": "Stan Man",
            "email": "stan@gmail.com",
            "phone": "1234567890",
            "password": "stan123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['id']

        # login to get token
        login_payload = {
            "email": "stan@gmail.com",
            "password": "stan123"
        }
        login_response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json['token']

        # update with token in header
        update_payload = {
            "name": "Stanley Man",
            "email": "stan@gmail.com",
            "phone": "1234567890",
            "password": "stan123"
        }
        response = self.client.put(
            '/customers/',
            json=update_payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], customer_id)
        self.assertEqual(response.json['name'], "Stanley Man")
        self.assertEqual(response.json['email'], "stan@gmail.com")

    def test_update_customer_unauthorized_no_token(self):
        customer_payload = {
            "name": "Stan Man",
            "email": "stan@gmail.com",
            "phone": "1234567890",
            "password": "stan123"
        }
        self.client.post('/customers/', json=customer_payload)

        update_payload = {
            "name": "Stanley Man",
            "email": "stan@gmail.com",
            "phone": "1234567890",
            "password": "stan123"
        }
        response = self.client.put('/customers/', json=update_payload)

        self.assertEqual(response.status_code, 400)

    def test_delete_customer_success(self):
        customer_payload = {
            "name": "Delete Me",
            "email": "delete@email.com",
            "phone": "1112223333",
            "password": "delete123"
        }
        self.client.post('/customers/', json=customer_payload)

        login_payload = {
            "email": "delete@email.com",
            "password": "delete123"
        }
        login_response = self.client.post('/customers/login', json=login_payload)
        token = login_response.json['token']

        response = self.client.delete(
            '/customers/',
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_customer_unauthorized_no_token(self):
        response = self.client.delete('/customers/')
        self.assertEqual(response.status_code, 400)

    def test_get_my_tickets_empty(self):
        customer_payload = {
            "name": "No Tickets",
            "email": "notickets@email.com",
            "phone": "7778889999",
            "password": "none123"
        }
        self.client.post('/customers/', json=customer_payload)

        login_payload = {
            "email": "notickets@email.com",
            "password": "none123"
        }
        login_response = self.client.post('/customers/login', json=login_payload)
        token = login_response.json['token']

        response = self.client.get(
            '/customers/my-tickets',
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)









