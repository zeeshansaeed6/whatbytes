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

    def test_doctor_readable_by_all_but_only_creator_can_modify(self):
        a, b = make_client('a@x.com'), make_client('b@x.com')
        body = {'name': 'D', 'specialization': 'Cardio', 'email': 'd@x.com'}
        d = a.post('/api/doctors/', body, format='json').data['id']
        self.assertEqual(b.get(f'/api/doctors/{d}/').status_code, 200)
        self.assertEqual(b.put(f'/api/doctors/{d}/', body, format='json').status_code, 403)
        self.assertEqual(b.delete(f'/api/doctors/{d}/').status_code, 403)
        self.assertEqual(a.put(f'/api/doctors/{d}/', {**body, 'name': 'D2'}, format='json').status_code, 200)
        self.assertEqual(a.delete(f'/api/doctors/{d}/').status_code, 204)

    def test_validation_errors(self):
        c = make_client('a@x.com')
        r = c.post('/api/patients/', {'name': 'P', 'age': -1}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('age', r.data)
        self.assertIn('gender', r.data)
        r = c.post('/api/doctors/', {'name': 'D', 'specialization': 'X', 'email': 'not-an-email'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('email', r.data)

    def test_register_validation_and_duplicate_email(self):
        c = APIClient()
        ok = {'name': 'N', 'email': 'a@x.com', 'password': 'pass12345'}
        self.assertEqual(c.post('/api/auth/register/', ok, format='json').status_code, 201)
        dup = c.post('/api/auth/register/', {**ok, 'email': 'A@X.com'}, format='json')  # case-insensitive
        self.assertEqual(dup.status_code, 400)
        self.assertIn('email', dup.data)
        short = c.post('/api/auth/register/', {**ok, 'email': 'b@x.com', 'password': 'short'}, format='json')
        self.assertEqual(short.status_code, 400)
        self.assertIn('password', short.data)

    def test_login_with_wrong_password_is_401(self):
        make_client('a@x.com')
        r = APIClient().post('/api/auth/login/', {'email': 'a@x.com', 'password': 'wrong'}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_cannot_map_or_read_another_users_patient(self):
        a, b = make_client('a@x.com'), make_client('b@x.com')
        p = a.post('/api/patients/', {'name': 'P', 'age': 30, 'gender': 'F'}, format='json').data['id']
        d = b.post('/api/doctors/', {'name': 'D', 'specialization': 'X', 'email': 'd@x.com'}, format='json').data['id']
        self.assertEqual(b.post('/api/mappings/', {'patient': p, 'doctor': d}, format='json').status_code, 400)
        self.assertEqual(b.get(f'/api/mappings/{p}/').status_code, 404)
        self.assertEqual(b.get('/api/mappings/').data, [])
