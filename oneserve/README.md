# OneServe - Unified Digital Platform for Government & Professional Services

A complete full-stack web application for managing government services including complaints, document storage (DigiLocker), and certificate applications.

## 🚀 Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Citizen, Officers, Admin)
- Secure password hashing with bcrypt

### Complaint Management Portal
- File complaints with title, description, place, and/or images
- Automatic category detection using image classification
- Text-based category assignment using keyword matching
- Auto-assignment to department officers
- Real-time status tracking (Pending → In Progress → Resolved/Rejected)
- Officer dashboard with complaint management
- Comment system for officer-citizen communication

### DigiLocker (Document Storage)
- Upload documents (PDF, images)
- OCR text extraction from images
- Automatic document type detection (Aadhaar, PAN)
- Secure document storage
- Pattern-based verification

### Certificate Application System
- Apply for multiple certificate types (Income, Domicile, Birth, Caste)
- Document attachment support
- Admin review and approval workflow
- Automatic PDF certificate generation
- Download approved certificates

### Dashboards & Analytics
- **Citizen Dashboard**: Complaint stats, application status, trends
- **Officer Dashboard**: Assigned complaints, resolution metrics
- **Admin Dashboard**: System overview, performance metrics
- Interactive charts using Recharts (Pie, Bar, Line charts)

### Notifications
- Real-time notifications for all activities
- Status updates, comments, approvals
- Unread count indicator
- Mark as read functionality

## 📁 Project Structure

```
oneserve/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── db/
│   │   ├── database.py        # Database configuration
│   │   ├── models.py          # SQLAlchemy models
│   │   └── seed.py            # Database seeding script
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── complaints.py      # Complaint management
│   │   ├── locker.py          # DigiLocker endpoints
│   │   ├── certificates.py    # Certificate management
│   │   ├── notifications.py   # Notification endpoints
│   │   └── dashboard.py       # Dashboard analytics
│   ├── schemas/
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── complaint_assignment.py  # Complaint routing
│   │   ├── image_classifier.py      # Image categorization
│   │   ├── ocr_service.py           # OCR text extraction
│   │   └── certificate_pdf.py       # PDF generation
│   ├── utils/
│   │   ├── jwt.py             # JWT token utilities
│   │   ├── hashing.py         # Password hashing
│   │   └── files.py           # File handling
│   └── uploads/               # File storage
│       ├── complaints/
│       ├── locker/
│       └── certificates/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.jsx           # React entry point
│   │   ├── App.jsx            # Main app component
│   │   ├── api/
│   │   │   └── axios.js       # API client configuration
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # Authentication context
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── StatCard.jsx
│   │   │   └── Charts.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── CitizenDashboard.jsx
│   │   │   ├── OfficerDashboard.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── Complaints/
│   │   │   ├── Locker/
│   │   │   ├── Certificates/
│   │   │   └── Notifications.jsx
│   │   └── styles/
│   │       └── index.css
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: SQLite with SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib + bcrypt
- **File Upload**: python-multipart
- **PDF Generation**: ReportLab
- **OCR**: EasyOCR (optional, with fallback)
- **Image Processing**: Pillow

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
cd /Users/harshitjindal/Oneserve/oneserve
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and seed data
python db/seed.py
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## ▶️ Running the Application

### Start Backend Server

```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate  # if not already activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

### Start Frontend Server

```bash
# From frontend directory (in a new terminal)
cd frontend
npm run dev
```

Frontend will run on: **http://localhost:5173**

## 👤 Default User Credentials

### Admin Account
- **Email**: `admin@oneserve.com`
- **Password**: `Admin@123`

### Test Citizen
- **Email**: `citizen@oneserve.com`
- **Password**: `Citizen@123`

### Officers
- **Water Dept**: `officer.water@oneserve.com` / `Officer@123`
- **Electricity Dept**: `officer.electricity@oneserve.com` / `Officer@123`
- **Road Dept**: `officer.road@oneserve.com` / `Officer@123`
- **Sanitation Dept**: `officer.sanitation@oneserve.com` / `Officer@123`

## 📱 Usage Guide

### For Citizens

1. **Register/Login**: Create account or login with credentials
2. **File Complaint**: 
   - Navigate to Complaints → New Complaint
   - Provide title, description, place, or upload image
   - System automatically categorizes and assigns to officer
3. **Track Complaints**: View status updates and officer comments
4. **Upload Documents**: Use DigiLocker to store important documents
5. **Apply for Certificates**: Submit certificate applications with required documents
6. **View Dashboard**: Monitor all activities and trends

### For Officers

1. **Login**: Use officer credentials
2. **View Assigned Complaints**: See all complaints in your department
3. **Update Status**: Change complaint status (Pending → In Progress → Resolved)
4. **Add Comments**: Communicate with citizens
5. **Upload Resolution Proof**: Attach proof when marking as resolved

### For Admin

1. **Login**: Use admin credentials
2. **System Overview**: View comprehensive dashboard with all metrics
3. **Review Certificate Applications**: Approve/reject applications
4. **Generate Certificates**: System automatically creates PDF certificates
5. **Manage Users**: Create officer accounts

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` for:
- CORS origins
- Server host/port

Edit `backend/utils/jwt.py` for:
- JWT secret key
- Token expiration time

### Frontend Configuration

Edit `frontend/src/api/axios.js` for:
- API base URL

Edit `frontend/vite.config.js` for:
- Development server port
- Proxy configuration

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register citizen
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user
- `POST /auth/create-officer` - Create officer (admin only)

### Complaints
- `POST /complaints/create` - File complaint
- `GET /complaints/my` - Get user's complaints
- `GET /complaints/assigned` - Get assigned complaints (officer)
- `GET /complaints/{id}` - Get complaint details
- `PATCH /complaints/{id}/status` - Update status (officer)
- `POST /complaints/{id}/comment` - Add comment (officer)

### DigiLocker
- `POST /locker/upload` - Upload document
- `GET /locker/list` - List documents
- `GET /locker/download/{id}` - Download document

### Certificates
- `POST /certificates/apply` - Apply for certificate
- `GET /certificates/my` - Get user's applications
- `GET /certificates/{id}` - Get application details
- `GET /certificates/admin/pending` - Get pending applications (admin)
- `PATCH /certificates/{id}/approve` - Approve/reject (admin)
- `GET /certificates/{id}/download` - Download certificate PDF

### Notifications
- `GET /notifications` - Get all notifications
- `PATCH /notifications/{id}/read` - Mark as read
- `PATCH /notifications/read-all` - Mark all as read
- `GET /notifications/unread-count` - Get unread count

### Dashboard
- `GET /dashboard/citizen` - Citizen dashboard stats
- `GET /dashboard/officer` - Officer dashboard stats
- `GET /dashboard/admin` - Admin dashboard stats

## 🗄️ Database Schema

- **users**: User accounts with roles
- **complaints**: Complaint records
- **complaint_comments**: Officer comments on complaints
- **locker_documents**: Stored documents
- **certificate_applications**: Certificate requests
- **certificate_documents**: Supporting documents
- **notifications**: User notifications

## 🎨 Features Highlights

### Smart Complaint Categorization
- **Image-based**: Upload image → ML model detects category → Auto-assign
- **Text-based**: Keywords in title/description → Category detection → Auto-assign
- Categories: Water, Electricity, Road, Sanitation, General

### OCR Document Processing
- Automatic text extraction from uploaded documents
- Aadhaar detection (Government of India + 12-digit pattern)
- PAN detection (5 letters + 4 digits + 1 letter pattern)
- Document verification

### Certificate Generation
- Professional PDF certificates using ReportLab
- Custom styling with government portal branding
- Unique verification codes
- Digital signature section

### Real-time Notifications
- Status change notifications
- Comment notifications
- Application status updates
- Unread count badge

## 🔒 Security Features

- JWT token-based authentication
- Bcrypt password hashing
- Role-based access control
- Protected routes
- CORS configuration
- File upload validation

## 🐛 Troubleshooting

### Backend Issues

**Database not found**:
```bash
cd backend
python db/seed.py
```

**Module not found**:
```bash
pip install -r requirements.txt
```

**Port already in use**:
```bash
# Change port in uvicorn command
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**Dependencies error**:
```bash
rm -rf node_modules package-lock.json
npm install
```

**API connection error**:
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

**Build errors**:
```bash
npm run build
```

## 📝 Notes

- OCR functionality requires EasyOCR library. If not installed, system uses fallback mode.
- Image classification uses placeholder logic. Integrate your YOLOv8 model in `services/image_classifier.py`.
- File uploads are stored locally in `backend/uploads/` directory.
- SQLite database file `oneserve.db` is created in the backend directory.

## 🎯 Production Deployment

### Backend
1. Change JWT secret key to a strong random value
2. Use PostgreSQL instead of SQLite
3. Configure environment variables
4. Set up proper CORS origins
5. Enable HTTPS
6. Use production WSGI server (Gunicorn)

### Frontend
1. Build production bundle: `npm run build`
2. Deploy `dist/` folder to hosting service
3. Update API base URL to production backend
4. Enable CDN for static assets

## 📄 License

This project is created for educational and demonstration purposes.

## 👨‍💻 Author

Built with ❤️ for OneServe Digital Platform

---

**🎉 Your OneServe platform is ready! Access the application at http://localhost:5173**
