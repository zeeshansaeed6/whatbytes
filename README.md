# Healthcare Backend

A REST API for managing patients, doctors and patient–doctor assignments.
Built with **Django**, **Django REST Framework**, **PostgreSQL** and **JWT authentication** (`djangorestframework-simplejwt`).

## Features
- Register and log in; JWT access/refresh tokens.
- Patients are private: each user only sees and edits their own.
- Doctors are visible to every authenticated user; only the creator can edit or delete them.
- Assign doctors to patients (duplicate assignments are rejected).
- Validation errors and proper HTTP status codes (400, 401, 404, ...).
- Secrets are read from environment variables, never committed.

## Quick start with Docker
```
docker compose up --build
```
This starts PostgreSQL and the API (migrations run automatically). The API is at http://localhost:8000/api/. No `.env` needed; demo credentials are in `docker-compose.yml`.

## Setup (without Docker)
1. Install Python 3.10+ and PostgreSQL, then create a database:
   ```
   createdb healthcare
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create your env file and fill in `SECRET_KEY` and the database credentials:
   ```
   cp .env.example .env
   ```
4. Run migrations and start the server:
   ```
   python manage.py migrate
   python manage.py runserver
   ```

## Environment variables
| Name | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, omit/`False` in production |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL credentials |
| `DB_HOST`, `DB_PORT` | Optional, default `localhost` / `5432` |

## API
All endpoints except register and login need the header `Authorization: Bearer <access_token>`.

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register/` | Body: `name, email, password` |
| POST | `/api/auth/login/` | Body: `email, password` -> `access, refresh` |
| POST | `/api/auth/refresh/` | Body: `refresh` -> new `access` |
| POST | `/api/patients/` | Add a patient |
| GET | `/api/patients/` | List your patients |
| GET / PUT / DELETE | `/api/patients/<id>/` | Your patient only (404 otherwise) |
| POST | `/api/doctors/` | Add a doctor |
| GET | `/api/doctors/` | List all doctors |
| GET | `/api/doctors/<id>/` | Doctor details |
| PUT / DELETE | `/api/doctors/<id>/` | Creator only (403 otherwise) |
| POST | `/api/mappings/` | Body: `patient, doctor` (patient must be yours) |
| GET | `/api/mappings/` | Mappings of your patients |
| GET | `/api/mappings/<patient_id>/` | Doctors assigned to that patient |
| DELETE | `/api/mappings/<id>/` | Remove a mapping |

### Example
```
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "email": "jane@example.com", "password": "pass12345"}'

curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "pass12345"}'

curl http://127.0.0.1:8000/api/patients/ -H "Authorization: Bearer <access_token>"
```

### Postman
Import `postman_collection.json`. Run **Register**, then **Login** (it saves the token automatically), then any other request.

### Postman test results
| Register (201) | Create patient (201) |
|---|---|
| ![Register](docs/screenshots/01-register-201.png) | ![Create patient](docs/screenshots/02-create-patient-201.png) |

| List patients (200) | Create doctor (201) |
|---|---|
| ![List patients](docs/screenshots/03-list-patients-200.png) | ![Create doctor](docs/screenshots/04-create-doctor-201.png) |

Assign doctor to patient (201):

![Assign doctor](docs/screenshots/05-assign-doctor-201.png)

## Tests
```
python manage.py test
```
Covers the full register -> login -> patient/doctor -> mapping flow, duplicate mappings, unauthenticated access and per-user data isolation.

## Project layout
```
config/   Django settings and root URLs
api/      models, serializers, views, urls, tests
```
