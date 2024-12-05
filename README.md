# Recruitment Platform

A full-stack recruitment platform built with Django and React, featuring Google OAuth authentication.

## Features

- Google OAuth2 Authentication
- JWT Token-based Authorization
- User Management
- Secure API Endpoints

## Tech Stack

- **Frontend**: React, @react-oauth/google
- **Backend**: Django, Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite (development)

## Setup

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
Create `.env` file in backend directory with:
```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
Create `.env` file in frontend directory with:
```
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

3. Start development server:
```bash
npm start
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
