# Legal Request Management System (LRMS)

A comprehensive Django-based web application for managing legal requests between departments and the legal team. This system streamlines the process of requesting legal assistance, document reviews, access permissions, and data breach notifications.

## 🚀 Features

### For Department Users
- **User Registration & Authentication**: Role-based login system
- **Ticket Creation**: Submit requests for legal assistance with dynamic form validation
- **Request Types Supported**:
  - **For Copy**: Request copies of legal documents
  - **For Review**: Submit contracts/agreements for legal review
  - **For Access**: Request access to systems or confidential documents
  - **For Data Breach Notification**: Report suspected or confirmed data breaches
- **Dashboard**: View all submitted tickets with status tracking
- **File Uploads**: Secure document attachment for review requests

### For Legal Admins
- **Admin Dashboard**: Comprehensive view of all tickets with filtering options
- **Ticket Processing**: Review, comment, and update ticket status
- **File Management**: Download user attachments and upload reviewed documents
- **Assignment System**: Assign tickets to specific legal team members
- **Priority Management**: Set priority levels for urgent requests
- **Advanced Filtering**: Filter by status, department, request type, and search terms

## 🛠️ Technology Stack

- **Backend**: Django 5.0.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5 + Custom CSS
- **Authentication**: Django's built-in auth with custom user roles
- **File Storage**: Local file system (configurable for cloud storage)
- **Icons**: Bootstrap Icons

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd LegalTicketingSystem
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 👥 User Accounts

### Default Test Accounts
- **Admin Account**: 
  - Username: `admin`
  - Password: `admin123`
  - Role: Legal Admin

- **Department User Account**:
  - Username: `user1`
  - Password: `user123`
  - Role: Department User

### Creating New Accounts
1. Visit `/auth/signup/` to create new accounts
2. Choose appropriate role during registration
3. Department Users can create tickets
4. Legal Admins can process tickets

## 📁 Project Structure

```
LegalTicketingSystem/
├── lrms_project/          # Django project settings
│   ├── settings.py       # Main configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI configuration
├── authentication/       # User management app
│   ├── models.py        # Custom User model
│   ├── views.py         # Auth views (login, signup)
│   ├── forms.py         # Registration forms
│   └── urls.py          # Auth URL patterns
├── tickets/             # Ticket management app
│   ├── models.py        # Ticket model
│   ├── views.py         # Ticket views (CRUD operations)
│   ├── forms.py         # Ticket forms
│   ├── decorators.py    # Permission decorators
│   └── urls.py          # Ticket URL patterns
├── templates/           # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── authentication/  # Auth templates
│   └── tickets/         # Ticket templates
├── static/              # Static files
│   ├── css/style.css    # Custom styles
│   └── js/ticket_form.js # Dynamic form JavaScript
├── media/               # Uploaded files
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔐 Security Features

- **Role-based Access Control**: Users can only access features appropriate to their role
- **File Upload Validation**: Secure file type and size validation
- **CSRF Protection**: All forms protected against cross-site request forgery
- **Permission Decorators**: Custom decorators for view-level security
- **Secure File Storage**: Uploaded files stored in secure media directory

## 📊 Request Types & Workflows

### 1. Request for Copy
- **Purpose**: Department requests copies of legal documents
- **Process**: Admin reviews → uploads document → marks approved/rejected
- **Required Fields**: Basic ticket information

### 2. Request for Review
- **Purpose**: Submit contracts/agreements for legal review
- **Process**: User uploads document → Admin reviews → uploads reviewed version
- **Required Fields**: Document attachment, contracting party details

### 3. Request for Access
- **Purpose**: Request access to systems or confidential documents
- **Process**: User justifies request → Admin approves/rejects with justification
- **Required Fields**: Basic ticket information, justification in remarks

### 4. Data Breach Notification
- **Purpose**: Report suspected or confirmed data breaches
- **Process**: User reports → Admin sets priority → investigation tracking
- **Required Fields**: Detailed breach information in remarks

## 🎨 User Interface

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern, professional styling
- **Color-coded Status**: Visual indicators for ticket status and priority
- **Interactive Forms**: Dynamic form fields based on request type
- **File Upload Interface**: Drag-and-drop file upload with validation

## 🔧 Configuration

### Database Configuration
For production, update `settings.py` to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### File Storage Configuration
For cloud storage (AWS S3, Google Cloud), update `settings.py`:

```python
# Add to settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'your_access_key'
AWS_SECRET_ACCESS_KEY = 'your_secret_key'
AWS_STORAGE_BUCKET_NAME = 'your_bucket_name'
```

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Set up proper database (PostgreSQL recommended)
4. Configure static file serving
5. Set up media file serving
6. Configure email settings for notifications
7. Set up SSL/HTTPS
8. Configure backup strategy

### Environment Variables
Create a `.env` file for sensitive settings:

```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📈 Future Enhancements

- **Email Notifications**: Automatic email alerts for status changes
- **Advanced Analytics**: Dashboard with charts and statistics
- **API Integration**: REST API for mobile apps or integrations
- **Workflow Automation**: Automated routing based on request type
- **Document Versioning**: Track document changes and versions
- **Audit Logging**: Comprehensive activity logging
- **Mobile App**: Native mobile application
- **Advanced Search**: Full-text search across tickets and documents

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**: 
   ```bash
   python manage.py makemigrations --empty app_name
   python manage.py migrate
   ```

2. **Static Files Not Loading**:
   ```bash
   python manage.py collectstatic
   ```

3. **Permission Errors**: Ensure proper file permissions for media directory

4. **Database Connection Issues**: Check database configuration and credentials

### Debug Mode
For development, ensure `DEBUG = True` in settings.py for detailed error messages.

## 📞 Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.

## 📄 License

This project is proprietary software. All rights reserved.

---

**Legal Request Management System** - Streamlining legal processes for modern organizations.




