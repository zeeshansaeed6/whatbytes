from django.test import TestCase
from rest_framework.test import APIClient


def make_client(email):
    c = APIClient()
    c.post('/api/auth/register/', {'name': 'N', 'email': email, 'password': 'pass12345'}, format='json')
    tok = c.post('/api/auth/login/', {'email': email, 'password': 'pass12345'}, format='json').data['access']
    c.credentials(HTTP_AUTHORIZATION=f'Bearer {tok}')
    return c


class FlowTest(TestCase):
    def test_full_flow(self):
        c = make_client('a@x.com')
        p = c.post('/api/patients/', {'name': 'P', 'age': 30, 'gender': 'F'}, format='json').data['id']
        d = c.post('/api/doctors/', {'name': 'D', 'specialization': 'Cardio', 'email': 'd@x.com'}, format='json').data['id']
        m = c.post('/api/mappings/', {'patient': p, 'doctor': d}, format='json')
        self.assertEqual(m.status_code, 201)
        self.assertEqual(c.post('/api/mappings/', {'patient': p, 'doctor': d}, format='json').status_code, 400)
        self.assertEqual(len(c.get(f'/api/mappings/{p}/').data), 1)
        self.assertEqual(c.delete(f"/api/mappings/{m.data['id']}/").status_code, 204)
        self.assertEqual(c.put(f'/api/patients/{p}/', {'name': 'P2', 'age': 31, 'gender': 'F'}, format='json').status_code, 200)

    def test_isolation_and_auth(self):
        a, b = make_client('a@x.com'), make_client('b@x.com')
        p = a.post('/api/patients/', {'name': 'P', 'age': 30, 'gender': 'F'}, format='json').data['id']
        self.assertEqual(APIClient().get('/api/patients/').status_code, 401)
        self.assertEqual(b.get(f'/api/patients/{p}/').status_code, 404)
        self.assertEqual(b.get('/api/patients/').data, [])
