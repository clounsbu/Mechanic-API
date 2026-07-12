from application import create_app
from application.models import db
import unittest


class TestItem(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()

    def _item_payload(self, item_name="Brake Pad", price=49.99):
        return {
            "item_name": item_name,
            "price": price
        }

    def test_create_item(self):
        response = self.client.post('/items/', json=self._item_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['item_name'], "Brake Pad")

    def test_create_item_missing_required_field(self):
        response = self.client.post('/items/', json={"price": 49.99})

        self.assertEqual(response.status_code, 400)

    def test_get_all_items(self):
        self.client.post('/items/', json=self._item_payload())

        response = self.client.get('/items/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(item['item_name'] == "Brake Pad" for item in response.json))

    def test_get_single_item(self):
        create_response = self.client.post('/items/', json=self._item_payload())
        item_id = create_response.json['id']

        response = self.client.get(f'/items/{item_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['item_name'], "Brake Pad")

    def test_get_single_item_not_found(self):
        response = self.client.get('/items/9999')

        self.assertEqual(response.status_code, 400)

    def test_update_item(self):
        create_response = self.client.post('/items/', json=self._item_payload())
        item_id = create_response.json['id']

        updated_payload = self._item_payload(item_name="Oil Filter", price=15.50)
        response = self.client.put(f'/items/{item_id}', json=updated_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['item_name'], "Oil Filter")

    def test_update_item_not_found(self):
        response = self.client.put('/items/9999', json=self._item_payload())

        self.assertEqual(response.status_code, 400)

    def test_delete_item(self):
        create_response = self.client.post('/items/', json=self._item_payload())
        item_id = create_response.json['id']

        response = self.client.delete(f'/items/{item_id}')

        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
