# Blog Management API

A FastAPI-based Blog Management API with authentication, social login, subscription-based access control, billing, comments, likes, email notifications, and invoice generation.

## Features

- User registration and authentication
- Auth0 authentication
- Google social login
- Facebook social login integration
- JWT-based authentication
- Protected API endpoints
- Blog post creation and management
- Post pagination and search
- Comments and comment management
- Like functionality
- Email notifications for new comments
- Subscription-based access control
- Multiple subscription plans
- Billing history
- PDF invoice generation
- Image upload for blog posts
- API documentation using Swagger UI
- SQLite/MySQL database support

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Auth0
- JWT
- SQLite / MySQL
- ReportLab
- SMTP
- HTML
- CSS
- JavaScript
- Swagger UI

## Project Structure

```text
blog-management-api/
│
├── app/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── auth/
│   ├── email_service.py
│   ├── database.py
│   └── main.py
│
├── media/
│   ├── invoices/
│   └── posts/
│
├── templates/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md