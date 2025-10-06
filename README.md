# 🛒 CustomyShop API

A backend e-commerce application built with Django + DRF + JWT Auth + Celery + Redis for managing users, stores, products, and orders.

## 📌 Features

- JWT-based authentication with OTP support
- User registration, login, profile, and address management
- Store creation and product management
- Shopping cart, order checkout, and online payment
- Background tasks using Celery + Redis
- Fully documented and tested API
- Customized Django Admin Panel


## 🛠 Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

## 🚀 Installation & Running

### 1- Clone the repository
```bash
git clone https://github.com/firooz-hosseini/CustomyShop.git
cd CustomyShop
```

### 2- Create virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # for Linux/macOS
.venv\Scripts\activate     # for Windows
pip install -r requirements.txt
```

### 3- Environment Variables
Create a `.env` file in the root directory and set the required values:

```bash
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

CORS_ALLOW_ALL_ORIGINS = True

DB_ENGINE=your_db_engine
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port

EMAIL_BACKEND=your_email_backend 
EMAIL_HOST=your_email_host
EMAIL_PORT=your_email_port
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password

ACCESS_TOKEN_LIFETIME = minutes
REFRESH_TOKEN_LIFETIME = days

CELERY_BROKER_URL = your_celery_broker_url
CELERY_RESULT_BACKEND = your_celery_result_backend

CACHE_LOCATION = your_cache_location

AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_storage_bucket_name
AWS_S3_ENDPOINT_URL=your_endpoint_url
AWS_S3_REGION_NAME=your_region_name
```

### 4- Apply Database Migrations
```bash
python manage.py migrate
```

### 5- Create Superuser
```bash
python manage.py createsuperuser
```

### 6- Running the Server
```bash
python manage.py runserver
```
Server will run at `http://127.0.0.1:8000`


### 7- Optional: Running with Docker
```bash
docker-compose up --build -d
```
This will start the web server, database, and Redis automatically.


## 🧪 Running Tests
```bash
python manage.py test
```
or with Docker:
```bash
docker-compose exec web python manage.py test
```


## 👨‍💻 Contributing

- Create a new branch for each feature:
```bash
git checkout -b feature/my-feature
```
- Submit a Pull Request after completing the feature.
