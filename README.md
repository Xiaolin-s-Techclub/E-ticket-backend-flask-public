# Electronic Ticket System - Backend

A Flask-based backend API for electronic ticket management system designed for music festivals and events.

## Overview

This system provides a backend service for event participants to apply for electronic tickets, receive them via email, and manage entry using QR codes. It integrates with PostgreSQL database and provides email functionality through AWS SES and Waypoint API.

## Key Features

- 🎫 **Electronic Ticket Application System** - Users can apply for participation through web forms
- 📧 **Automated Email Delivery** - Automatic distribution of tickets with QR codes
- 🔍 **QR Code Generation & Verification** - Unique QR codes for entry management
- 👥 **User Management** - Permission management for students, teachers, and administrators
- 📊 **Participant Analytics** - Analysis of event participation status
- 🎭 **Multi-Event Support** - Reusable for different events

## System Requirements

- Python 3.9+
- PostgreSQL 12+
- Redis (for session management)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Xiaolin-s-Techclub/E-ticket-backend-flask-public.git
cd E-ticket-backend-flask-public
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup

Copy `.env.example` to `.env` and configure the required values:

```bash
cp .env.example .env
```

Edit the `.env` file with the following values:

```env
# Database Configuration
DB_USER=your_db_username
DB_USER_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=music_fes
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Email Configuration
FROM_EMAIL=noreply@yourdomain.com
CONTACT_EMAIL=support@yourdomain.com

# AWS SES Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=ap-northeast-1

# Waypoint API Configuration
WAYPOINT_API_UNAME=your_waypoint_username
WAYPOINT_API_PASS=your_waypoint_password

# Application Configuration
CUSTOM_HASH_STRING=your_custom_hash_string
SERVER_URL=https://yourdomain.com/
FLASK_SECRET_KEY=your_flask_secret_key_here

# Development vs Production
DEV_MODE=True  # Set to False for production
```

### 5. Database Setup

Start your PostgreSQL server and create the database:

```sql
CREATE DATABASE music_fes;
```

The required tables will be created automatically when you start the application.

### 6. Run the Application

```bash
python backend/src/app.py
```

The development server will start at `http://localhost:5000`.

## API Endpoints

### Ticket Application
- `POST /api/v1/apply` - Submit new ticket application
- `GET /apply/student` - Student application form
- `GET /apply/teacher` - Teacher application form

### Administration
- `GET /admin/dashboard` - Administrator dashboard
- `GET /admin/analytics` - Participant statistics
- `POST /admin/send-tickets` - Bulk ticket distribution

### User Management
- `POST /api/v1/login` - User login
- `GET /api/v1/users` - Get user list

For detailed API specifications, refer to `api-document.yml`.

## Deployment

### Heroku
1. Create a Heroku app
2. Add PostgreSQL and Redis addons
3. Set environment variables
4. `git push heroku main`

### Docker
```bash
docker build -t e-ticket-backend .
docker run -p 5000:5000 --env-file .env e-ticket-backend
```

### DigitalOcean App Platform
Configure App Specification based on `heroku.yml` and deploy

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Connection Test
```bash
python test_db_conn.py
```

### Development Mode
```bash
export DEV_MODE=True
python backend/src/app.py
```

## Security

This repository has undergone security cleanup for public release:

- 🔒 All credentials moved to environment variables
- 🚫 Removed `.env` file and credentials directory
- 📝 Comprehensive `.gitignore` prevents future credential leaks
- 🔐 Flask secret key changed from hardcoded to environment variable
- 📚 Provided `.env.example` as configuration template

For details, see `SECURITY_CLEANUP.md`.

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── config/         # Configuration files
│   │   ├── model/          # Data models
│   │   ├── service/        # Business logic
│   │   ├── api.py          # API endpoints
│   │   └── app.py          # Main application
│   ├── outputs/            # Generated ticket images
│   └── references/         # Ticket templates
├── frontend/
│   ├── templates/          # HTML templates
│   └── static/            # CSS, JavaScript
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── api-document.yml       # API specification
```

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is released under the MIT License.

## Support

For questions and bug reports, please use [Issues](https://github.com/Xiaolin-s-Techclub/E-ticket-backend-flask-public/issues).

---

**Development Team**: Xiaolin's TechClub  
**Contact**: xiaolinstechclub@gmail.com