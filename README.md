# 🛒 CustomyShop API

**A modern e-commerce backend** built with **Django REST Framework**, **JWT Authentication**, **Celery**, and **Redis** — designed for managing users, stores, products, and orders with full scalability and modularity.

---

## 📋 Table of Contents
- [📌 Features](#-features)
- [🧠 Tech Stack](#-tech-stack)
- [🛠 Prerequisites](#-prerequisites)
- [🚀 Installation & Running](#-installation--running)
- [📖 API Documentation](#-api-documentation)
- [🧪 Running Tests](#-running-tests)
- [👨‍💻 Contributing](#-contributing)
- [🪪 License](#-license)
- [📬 Contact](#-contact)

---

## 📌 Features

- 🔐 **JWT-based authentication** with OTP (One-Time Password) support  
- 👤 **User management:** registration, login, profile, and address  
- 🏬 **Store and product management** system  
- 🛒 **Shopping cart** and **order checkout**  
- 💳 **Online payment integration**  
- Pagination, filtering, and search for API endpoints
- Email integration for notifications (Gmail SMTP)
- AWS S3 support for media files
- ⚙️ **Celery + Redis** for background tasks  
- 📚 **Comprehensive API documentation**  
- 🧩 **Custom Django Admin Panel** for intuitive management  
- ✅ **Unit and integration tests**

---

## 🧠 Tech Stack

| Category | Technologies |
|-----------|---------------|
| **Backend** | Python, Django, Django REST Framework |
| **Auth** | JWT, SimpleJWT, Custom OTP |
| **API Docs** | Swagger DRF Spectacular |
| **Database** | PostgreSQL |
| **Async Tasks** | Celery + Redis |
| **Cache** | Redis |
| **Storage** | Local + AWS S3 (boto3, django-storages) |
| **Deployment** | Docker, Docker Compose |
| **Testing** | Django Test Framework |

---

## 🛠 Prerequisites

- Python **3.12+**
- **Docker** & **Docker Compose**
- **Git**

---

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
CORS_ALLOW_ALL_ORIGINS=True

DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password

ACCESS_TOKEN_LIFETIME=30  # minutes
REFRESH_TOKEN_LIFETIME=7  # days

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CACHE_LOCATION=redis://redis:6379/1

AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_ENDPOINT_URL=https://s3.your-region.amazonaws.com
AWS_S3_REGION_NAME=your_region
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


### 🐳 Optional: Running with Docker
```bash
docker-compose up --build -d
```
This will automatically start the **web**, **database**, **Celery** and **Redis** services.

---

## 📖 API Documentation

Interactive API docs available at:

- Swagger UI → `/api/swagger/`
- ReDoc → `/api/redoc/`
- DRF Browsable API → `/api/`

---

## 🧪 Running Tests
```bash
python manage.py test
```

### Docker
```bash
docker-compose exec web python manage.py test
```


## 👨‍💻 Contributing

Contributions are welcome! 🎉  
To add a new feature or fix a bug:
1. **Fork** the repository
2. **Create a feature branch** for your changes (`git checkout -b feature/your-feature`)
3. **Commit your changes** with clear messages (`git commit -m "Add feature"`)
4. **Push** your branch to your fork (`git push origin feature/your-feature`)
5. **Open a Pull Request** for review
6. **Participate in the review process** and make requested changes
7. **Merge** will be done after approval

---

## 🪪 License

For educational use.

---

## 📬 Contact

Created by **[Firooz Hosseini](https://www.linkedin.com/in/firooz-hosseini)**  
📧 Email: [firooz.hosseini@ut.ac.ir](mailto:firooz.hosseini@ut.ac.ir)

---

> ⭐ *If you like this project, consider giving it a star on GitHub!*
