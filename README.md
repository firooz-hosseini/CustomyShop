# 🛒 CustomyShop API

A backend e-commerce application built with Django + DRF + JWT Auth + Celery + Redis for managing users, stores, products, and orders.

## 📌 Features

- JWT-based authentication with OTP support
- User registration, login, profile, and address management
- Store creation and product management
- Shopping cart, order checkout, and online payment (Zarinpal)
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

SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=your_db_engine
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST='localhost'
DB_PORT=your_db_port


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
