# Healthcare Backend

Django + DRF + PostgreSQL + JWT (simplejwt).

## Setup
```
pip install -r requirements.txt
cp .env.example .env      # fill in SECRET_KEY and Postgres credentials
python manage.py migrate
python manage.py runserver
```

## Endpoints (all except register/login need `Authorization: Bearer <access>`)
| Method | Path | Notes |
|---|---|---|
| POST | /api/auth/register/ | `name, email, password` |
| POST | /api/auth/login/ | `email, password` -> `access, refresh` |
| POST | /api/auth/refresh/ | `refresh` -> new `access` |
| POST/GET | /api/patients/ | GET lists only your patients |
| GET/PUT/DELETE | /api/patients/<id>/ | own patients only |
| POST/GET | /api/doctors/ | GET lists all doctors |
| GET/PUT/DELETE | /api/doctors/<id>/ | modify only if creator |
| POST/GET | /api/mappings/ | `patient, doctor`; GET lists mappings of your patients |
| GET | /api/mappings/<patient_id>/ | doctors assigned to that patient |
| DELETE | /api/mappings/<id>/ | remove a mapping |

## Tests
`python manage.py test` (needs the Postgres DB from `.env`; the test DB is created automatically).
