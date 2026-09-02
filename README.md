 🚀 SOCIO — Photo & Video Sharing Platform

SOCIO is a full-stack social media application built with **FastAPI** and **Streamlit**. The application allows users to register, authenticate, upload photos and videos, view a social feed, and manage their own posts.

The backend is built using modern asynchronous Python technologies and uses **MySQL** for data persistence and **ImageKit** for cloud-based media storage.

---

✨ Features

- 🔐 User Registration and Authentication
- 🔑 JWT-based Authentication
- 🔒 Protected API Endpoints
- 📧 User Account Management
- 🖼️ Image Upload Support
- 🎥 Video Upload Support
- ☁️ Cloud Media Storage using ImageKit
- 📰 Social Media Feed
- 🗑️ Delete Your Own Posts
- 👤 Post Ownership Validation
- ⚡ Asynchronous Database Operations
- 📖 Interactive API Documentation with Swagger

---

 🛠️ Tech Stack

-----> Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- FastAPI Users
- JWT Authentication

-----> Database

- MySQL
- Async SQLAlchemy
- aiomysql

# Media Storage

- ImageKit

# Frontend

- Streamlit

# Deployment

- Railway

---

# 📂 Project Structure

```text
SOCIO/
│
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── frontend.py
│   ├── images.py
│   ├── main.py
│   ├── schemas.py
│   └── users.py
│
├── .env
├── .gitignore
├── railway.json
├── requirements.txt
└── README.md

⚙️ Installation
1. Clone the Repository
git clone https://github.com/BipinFaye/SOCIO--photo-and-video-sharing-REST-API-FAST-API-Backend.git

Navigate to the project directory:

cd SOCIO--photo-and-video-sharing-REST-API-FAST-API-Backend
2. Create a Virtual Environment
python -m venv .venv

Activate the virtual environment.

Windows
.venv\Scripts\activate
macOS / Linux
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root directory.

DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name

JWT_SECRET=your_secret_key

IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key

⚠️ Never commit your .env file to GitHub.

🗄️ Database

SOCIO uses MySQL with asynchronous SQLAlchemy support.

The application automatically creates the required database tables during startup.

The database connection is handled using:

SQLAlchemy Async Engine
aiomysql
AsyncSession
▶️ Running the Backend

Start the FastAPI application using:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000
📖 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI
http://127.0.0.1:8000/docs
ReDoc
http://127.0.0.1:8000/redoc
🖥️ Running the Frontend

In a separate terminal, run:

streamlit run app/frontend.py

The Streamlit application will typically be available at:

http://localhost:8501

Make sure the FastAPI backend is running before starting or using the frontend.

Local Architecture
┌──────────────────────┐
│   Streamlit Frontend │
│   localhost:8501     │
└──────────┬───────────┘
           │
           │ HTTP Requests
           ▼
┌──────────────────────┐
│   FastAPI Backend    │
│   localhost:8000     │
└──────────┬───────────┘
           │
           ├───────────────┐
           ▼               ▼
┌────────────────┐  ┌────────────────┐
│     MySQL      │  │    ImageKit    │
│    Database    │  │ Cloud Storage  │
└────────────────┘  └────────────────┘

🔗 API Endpoints
-------------------------------
Authentication
Method	Endpoint	Description
POST	/auth/register	Register a new user
POST	/auth/jwt/login	Login and receive JWT token
POST	/auth/jwt/logout	Logout user
POST	/auth/forgot-password	Request password reset
POST	/auth/reset-password	Reset password
POST	/auth/request-verify-token	Request verification token
POST	/auth/verify	Verify user
Users
Method	Endpoint	Description
GET	/users/me	Get current user information
PATCH	/users/me	Update current user information
GET	/users/{id}	Get user information
Posts
Method	Endpoint	Description
POST	/upload	Upload an image or video
GET	/feed	Get all posts
DELETE	/delete/{post_id}	Delete your own post


📤 Media Upload Flow
-------------------------------------

SOCIO does not permanently store uploaded media on the application server.

The upload process works as follows:

User Uploads File
        │
        ▼
FastAPI Receives File
        │
        ▼
Temporary File Created
        │
        ▼
File Uploaded to ImageKit
        │
        ▼
Media URL Stored in MySQL
        │
        ▼
Temporary File Deleted

This architecture makes the application more suitable for cloud deployment because uploaded media is stored separately from the application server.


🔒 Authentication
------------------------------------------------

SOCIO uses JWT-based authentication.

Protected endpoints require an authenticated user.

Example request header:

Authorization: Bearer <access_token>

Authentication and user management are implemented using FastAPI Users.


🛡️ Post Ownership
---------------------------------

Users can only delete posts that belong to their own account.

Before deleting a post, the application verifies that:

Authenticated User ID == Post Owner ID

If the user does not own the post, the API returns:

403 Forbidden


🚄 Deployment
------------------------------------

The backend is configured for deployment on Railway.

The application start command is:

uvicorn app.main:app --host 0.0.0.0 --port $PORT

Environment variables such as database credentials, JWT secrets, and ImageKit credentials should be configured through Railway environment variables.

Deployment Architecture
GitHub Repository
        │
        ▼
Railway FastAPI Service
        │
        ├───────────────┐
        ▼               ▼
Railway MySQL       ImageKit
Database           Cloud Storage


🌐 Live Demo
------------------------------------

🚧 Deployment in progress.

Backend API:

Coming Soon

Swagger Documentation:

Coming Soon
🚀 Future Improvements
❤️ Like and unlike posts
💬 Comments
👥 Follow and unfollow users
🔍 User search
🖼️ User profile pictures
🔔 Notifications
📱 Improved responsive frontend
🐳 Docker containerization
🔄 CI/CD pipeline
📊 Analytics dashboard


👨‍💻 Author
------------------

Harsh Faye

GitHub: BipinFaye

📄 License

This project is currently intended for educational and portfolio purposes.
