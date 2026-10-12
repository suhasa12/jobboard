# JobBoard & Applicant Tracking System (ATS)

A modern, production-ready, full-stack recruitment platform and Applicant Tracking System (ATS) built with **Python 3.10+**, **Django 5.x**, **SQLite**, and **Bootstrap 5**, prepared for seamless deployment to **Render**.

---

## 1. Project Overview & Features

### For Candidates
- **Discover Roles:** Search job postings by keywords, locations, job types, and skills.
- **Instant Client-Side Filtering:** Real-time JavaScript search and skill tag filtering without reloading the page.
- **Application Submission:** Apply through a modern Bootstrap 5 modal or standalone form with automatic contact pre-filling.
- **Strict Duplicate Prevention:** Zero duplicate applications enforced at both the Django server view level and the database level (`UniqueConstraint`).
- **Profile Management:** Candidates can maintain and edit their own contact details, portfolio links, and technical skillsets.
- **Application Tracking:** Track your hiring pipeline with status badges: `Applied`, `Under Review`, `Shortlisted`, and `Rejected`.

### For Recruiters (Staff Users)
- **Interactive ATS Dashboard:** Real-time metric cards for `Total Applications`, `Applied`, `Under Review`, `Shortlisted`, and `Rejected`.
- **Pipeline Stage Management:** Review candidate resumes, cover letters, and contact info; update application statuses with immediate feedback.
- **Job Posting Management:** Create, edit, and toggle active/inactive status for job postings.
- **Security & Authorization:** Enforced staff-only permissions with custom 403 Forbidden protection.

### For Administrators
- Full Django Admin integration for Companies, Job Postings, Candidates, and Applications.

---

## 2. Technology Stack

- **Backend:** Python 3.10+ & Django 5.x ORM
- **Database:** SQLite (`db.sqlite3`)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons
- **Static File Handling:** WhiteNoise (configured immediately after `SecurityMiddleware`)
- **Production Server:** Gunicorn WSGI
- **Deployment Platform:** Render (using `render.yaml`)

---

## 3. Project Structure

```text
jobboard/
├── manage.py
├── requirements.txt
├── render.yaml
├── .gitignore
├── README.md
├── jobboard_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── jobs/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    ├── management/
    │   └── commands/
    │       └── load_sample_data.py
    ├── templates/
    │   └── jobs/
    │       ├── base.html
    │       ├── home.html
    │       ├── job_list.html
    │       ├── job_detail.html
    │       ├── apply.html
    │       ├── candidate_profile.html
    │       ├── my_applications.html
    │       ├── recruiter_dashboard.html
    │       ├── manage_jobs.html
    │       ├── job_form.html
    │       ├── application_detail.html
    │       ├── login.html
    │       ├── register.html
    │       ├── 403.html
    │       └── 404.html
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            └── main.js
```

---

## 4. Local Setup Guide (Windows)

Follow these exact steps from inside the `jobboard` directory containing `manage.py`:

### Step 1: Open Terminal and Navigate to the Project Directory
```powershell
cd c:\Users\charan\Desktop\django1\jobboard
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Load Demonstration Data
Load 5 realistic tech companies, 16 job postings across different job types, candidate profiles, and multi-stage applications:
```powershell
python manage.py load_sample_data
```
*(This command is safe and idempotent—it can be executed multiple times without generating duplicates).*

### Step 6: Create an Administrator / Recruiter Account
```powershell
python manage.py createsuperuser
```
Follow the interactive prompts to set your administrator username, email, and password. Staff credentials grant access to both the **Recruiter ATS Dashboard** (`/recruiter/`) and **Django Admin** (`/admin/`).

### Step 7: Launch the Local Development Server
```powershell
python manage.py runserver
```

Open your browser at:
**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 5. User Roles and Key Workflows

### Candidate Experience
1. Navigate to **Browse Jobs** (`/jobs/`).
2. Type in the **Instant Live Search** bar or click any **Skill Tag** (e.g. `Python`, `Django`, `React`) to watch the cards filter dynamically without a page reload.
3. Click **View Details** or **Apply Now**.
4. Register a new candidate account at `/register/` or sign in at `/login/`.
5. Submit your application and cover letter.
6. Verify duplicate prevention by trying to re-apply for the same position.
7. Track your application status under **My Applications** (`/my-applications/`).
8. Update your contact information and skills in **Profile** (`/profile/`).

### Recruiter & Staff Experience
1. Log in with your staff/superuser account.
2. Visit **Recruiter Portal > ATS Dashboard** (`/recruiter/`).
3. View application metrics (`Total`, `Applied`, `Under Review`, `Shortlisted`, `Rejected`).
4. Update candidate statuses directly from the pipeline table or click **Review** to read full candidate statements.
5. Visit **Manage Jobs** (`/recruiter/jobs/`) to publish new job openings, edit descriptions, or toggle active/inactive status.

---

## 6. Render Deployment Guide

This project is pre-configured for automated continuous deployment on [Render](https://render.com) using GitHub and `render.yaml`.

### 1. Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit of JobBoard ATS"
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render
1. Sign in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository containing `render.yaml`.
4. Render will automatically detect the settings:
   - **Runtime:** `python`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn jobboard_project.wsgi:application`
5. Click **Apply**. Render will install requirements, collect static files with WhiteNoise, run migrations, and launch Gunicorn.

### 3. Production Settings & Security Notes
- `DEBUG=False` is set in production via environment variable.
- WhiteNoise serves static assets efficiently without needing external S3 buckets.
- Render automatically generates a unique `SECRET_KEY`.
- `ALLOWED_HOSTS` includes `.onrender.com` and automatically includes `RENDER_EXTERNAL_HOSTNAME`.
- **SQLite Note for Render:** Free Render Web Services use an ephemeral filesystem, meaning SQLite databases reset when instances spin down. For persistent SQLite data on Render, attach a [Render Persistent Disk](https://render.com/docs/disks) mounted to `/data` and point `DATABASES['default']['NAME']` to `/data/db.sqlite3`.

---

## 7. Troubleshooting Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Port 8000 already in use` | Another service is using port 8000 | Run `python manage.py runserver 8080` and open `http://127.0.0.1:8080/`. |
| `Permission Denied (403)` | Accessing recruiter pages as non-staff | Log in with a staff/superuser account created via `createsuperuser`. |
| Static files not updating | Browser cache | Hard refresh using `Ctrl + F5` (or `Cmd + Shift + R`). |
| Missing table errors | Migrations not run | Run `python manage.py makemigrations` followed by `python manage.py migrate`. |
| Duplicate application rejected | Candidate re-applying to same role | Intended behavior; candidates cannot submit duplicate applications for the same job. |
