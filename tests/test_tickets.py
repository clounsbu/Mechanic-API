from datetime import date
import unittest

from application import create_app
from application.models import Customer, Item, Mechanic, db


class TestTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()

    def _create_customer(self, email="customer@example.com", phone="5551112222"):
        with self.app.app_context():
            customer = Customer(
                name="Ticket Customer",
                email=email,
                phone=phone,
                password="secret123"
            )
            db.session.add(customer)
            db.session.commit()
            return customer.id

    def _create_mechanic(self, email="mech@example.com", phone="5553334444"):
        with self.app.app_context():
            mechanic = Mechanic(
                name="Ticket Mechanic",
                email=email,
                phone=phone,
                salary="55000"
            )
            db.session.add(mechanic)
            db.session.commit()
            return mechanic.id

    def _create_item(self):
        with self.app.app_context():
            item = Item(item_name="Brake Pad", price=49.99)
            db.session.add(item)
            db.session.commit()
            return item.id

    def _ticket_payload(self, customer_id):
        return {
            "service_date": str(date.today()),
            "vin": "1HGCM82633A123456",
            "service_desc": "Oil change",
            "customer_id": customer_id
        }

    def test_create_ticket(self):
        customer_id = self._create_customer()

        response = self.client.post('/tickets/', json=self._ticket_payload(customer_id))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['customer_id'], customer_id)

    def test_create_ticket_missing_customer_id(self):
        customer_id = self._create_customer()
        payload = self._ticket_payload(customer_id)
        payload.pop('customer_id')

        response = self.client.post('/tickets/', json=payload)

        self.assertEqual(response.status_code, 400)

    def test_get_all_tickets(self):
        customer_id = self._create_customer()
        self.client.post('/tickets/', json=self._ticket_payload(customer_id))

        response = self.client.get('/tickets/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_get_single_ticket(self):
        customer_id = self._create_customer()
        create_response = self.client.post('/tickets/', json=self._ticket_payload(customer_id))
        ticket_id = create_response.json['id']

        response = self.client.get(f'/tickets/{ticket_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], ticket_id)

    def test_get_single_ticket_not_found(self):
        response = self.client.get('/tickets/9999')

        self.assertEqual(response.status_code, 400)

    def test_update_ticket(self):
        customer_id = self._create_customer()
        create_response = self.client.post('/tickets/', json=self._ticket_payload(customer_id))
        ticket_id = create_response.json['id']

        updated_payload = {
            "service_date": str(date.today()),
            "vin": "2HGFA16558H654321",
            "service_desc": "Brake inspection",
            "customer_id": customer_id
        }
        response = self.client.put(f'/tickets/{ticket_id}', json=updated_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['vin'], "2HGFA16558H654321")
        self.assertEqual(response.json['service_desc'], "Brake inspection")

    def test_update_ticket_not_found(self):
        customer_id = self._create_customer()
        response = self.client.put('/tickets/9999', json=self._ticket_payload(customer_id))

        self.assertEqual(response.status_code, 400)

    def test_edit_ticket_mechanics_add_and_remove(self):
        customer_id = self._create_customer()
        mechanic_id = self._create_mechanic()
        create_response = self.client.post('/tickets/', json=self._ticket_payload(customer_id))
        ticket_id = create_response.json['id']

        add_response = self.client.put(
            f'/tickets/{ticket_id}/edit',
            json={"add_ids": [mechanic_id], "remove_ids": []}
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(len(add_response.json['mechanics']), 1)

        remove_response = self.client.put(
            f'/tickets/{ticket_id}/edit',
            json={"add_ids": [], "remove_ids": [mechanic_id]}
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertEqual(len(remove_response.json['mechanics']), 0)

    def test_edit_ticket_mechanics_ticket_not_found(self):
        response = self.client.put('/tickets/9999/edit', json={"add_ids": [1], "remove_ids": []})

        self.assertEqual(response.status_code, 400)

    def test_add_part_to_ticket(self):
        customer_id = self._create_customer()
        item_id = self._create_item()
        create_response = self.client.post('/tickets/', json=self._ticket_payload(customer_id))
        ticket_id = create_response.json['id']

        response = self.client.put(f'/tickets/{ticket_id}/add-part', json={"item_id": item_id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['item']), 1)

    def test_add_part_to_ticket_item_not_found(self):
        customer_id = self._create_customer()
        create_response = self.client.post('/tickets/', json=self._ticket_payload(customer_id))
        ticket_id = create_response.json['id']

        response = self.client.put(f'/tickets/{ticket_id}/add-part', json={"item_id": 9999})

        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
