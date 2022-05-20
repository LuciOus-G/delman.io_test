import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(THIS_DIR, os.pardir))


from app import app
import unittest

class unittesting(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_doctor(self):
        tester = app.test_client(self)
        response = tester.get('/doctors', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_employees(self):
        tester = app.test_client(self)
        response = tester.get('/employees', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_appointment(self):
        tester = app.test_client(self)
        response = tester.get('/appointment', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_patients(self):
        tester = app.test_client(self)
        response = tester.get('/patients', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='application/json')
        self.assertEqual(response.status_code, 405)

if __name__ == '__main__':
    unittest.main()
