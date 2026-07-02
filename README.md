# 🏥 Healthcare Backend API

A REST API for managing patients, doctors, and appointments — built with Django & PostgreSQL.

## 🛠️ Tech Stack

- **Python** + **Django 4.2**
- **Django REST Framework** — REST API
- **Simple JWT** — JWT Authentication
- **PostgreSQL** — Database

## 🔗 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | ❌ | Register user |
| POST | `/api/auth/login/` | ❌ | Login & get token |
| GET/POST | `/api/patients/` | ✅ | List / Create patients |
| GET/PUT/DELETE | `/api/patients/<id>/` | ✅ | Patient detail |
| GET/POST | `/api/doctors/` | ✅ | List / Create doctors |
| GET/PUT/DELETE | `/api/doctors/<id>/` | ✅ | Doctor detail |
| GET/POST | `/api/mappings/` | ✅ | List / Create mappings |
| GET/DELETE | `/api/mappings/<id>/` | ✅ | Mapping detail |

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/healthcare-backend.git
cd healthcare-backend
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
Create a `.env` file in the root directory:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=healthcare
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the server
```bash
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

## 🔐 Authentication

This API uses **JWT (JSON Web Token)** authentication.

1. Register at `/api/auth/register/`
2. Login at `/api/auth/login/` to get your token
3. Add to all protected requests:
   ```
   Authorization: Bearer <your_access_token>
   ```

## 📋 Sample Request Bodies

### Register
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass@123"
}
```

### Add Doctor
```json
{
    "name": "Dr. Smith",
    "email": "drsmith@example.com",
    "specialization": "Cardiology"
}
```

### Add Patient
```json
{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 30,
    "gender": "Female",
    "medical_history": "Diabetes"
}
```

### Map Patient to Doctor
```json
{
    "patient": 1,
    "doctor": 1
}
```
