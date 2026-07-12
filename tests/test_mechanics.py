from application import create_app
from application.models import db
import unittest


class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()

    def _mechanic_payload(self, email="mike@example.com", phone="5551234567"):
        return {
            "name": "Mike Fixer",
            "email": email,
            "phone": phone,
            "salary": "55000"
        }

    def test_create_mechanic(self):
        response = self.client.post('/mechanics/', json=self._mechanic_payload())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Mike Fixer")

    def test_create_mechanic_duplicate_email(self):
        first_response = self.client.post('/mechanics/', json=self._mechanic_payload())
        second_response = self.client.post(
            '/mechanics/',
            json=self._mechanic_payload(phone="5557778888")
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 400)

    def test_get_all_mechanics(self):
        self.client.post('/mechanics/', json=self._mechanic_payload())

        response = self.client.get('/mechanics/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(mechanic['name'] == "Mike Fixer" for mechanic in response.json))

    def test_get_single_mechanic(self):
        create_response = self.client.post('/mechanics/', json=self._mechanic_payload())
        mechanic_id = create_response.json['id']

        response = self.client.get(f'/mechanics/{mechanic_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], "mike@example.com")

    def test_get_single_mechanic_not_found(self):
        response = self.client.get('/mechanics/9999')

        self.assertEqual(response.status_code, 400)

    def test_update_mechanic(self):
        create_response = self.client.post('/mechanics/', json=self._mechanic_payload())
        mechanic_id = create_response.json['id']

        update_payload = {
            "name": "Michael Fixer",
            "email": "mike@example.com",
            "phone": "5551234567",
            "salary": "60000"
        }
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Michael Fixer")
        self.assertEqual(response.json['salary'], "60000")

    def test_update_mechanic_not_found(self):
        update_payload = {
            "name": "Ghost Mechanic",
            "email": "ghost@example.com",
            "phone": "5551112222",
            "salary": "60000"
        }
        response = self.client.put('/mechanics/9999', json=update_payload)

        self.assertEqual(response.status_code, 400)

    def test_delete_mechanic(self):
        create_response = self.client.post('/mechanics/', json=self._mechanic_payload())
        mechanic_id = create_response.json['id']

        response = self.client.delete(f'/mechanics/{mechanic_id}')

        self.assertEqual(response.status_code, 200)

    def test_delete_mechanic_not_found(self):
        response = self.client.delete('/mechanics/9999')

        self.assertEqual(response.status_code, 400)

    def test_get_mechanics_ranked(self):
        self.client.post('/mechanics/', json=self._mechanic_payload(email="a@example.com", phone="5550000001"))
        self.client.post('/mechanics/', json=self._mechanic_payload(email="b@example.com", phone="5550000002"))

        response = self.client.get('/mechanics/ranked/by-tickets')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)


if __name__ == '__main__':
    unittest.main()
