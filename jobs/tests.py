from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError

from .models import Company, JobPosting, Candidate, JobApplication


class JobBoardTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Company
        self.company = Company.objects.create(
            name="Acme Tech Innovations",
            location="San Francisco, CA",
            website="https://acme.example.com",
            description="Innovative cloud software company."
        )

        # Create Job Posting
        self.job = JobPosting.objects.create(
            company=self.company,
            title="Senior Python Architect",
            job_type="Full-time",
            required_skills="Python, Django, PostgreSQL, Docker",
            salary_range="$140,000 - $170,000",
            description="Lead backend API architecture and high-scale services.",
            active=True
        )

        # Inactive Job Posting
        self.inactive_job = JobPosting.objects.create(
            company=self.company,
            title="Archived Role",
            job_type="Contract",
            required_skills="Go",
            salary_range="$100k",
            description="Old listing",
            active=False
        )

        # Regular Candidate User
        self.candidate_user = User.objects.create_user(
            username="candidate_user",
            email="candidate@example.com",
            password="SecurePassword123!"
        )
        self.candidate = Candidate.objects.create(
            user=self.candidate_user,
            full_name="Alice Candidate",
            email="candidate@example.com",
            phone="+1 (555) 123-4567",
            skills="Python, Django"
        )

        # Staff / Recruiter User
        self.staff_user = User.objects.create_user(
            username="recruiter_staff",
            email="recruiter@example.com",
            password="StaffPassword123!",
            is_staff=True
        )

    # 1. Public Pages
    def test_home_page_loads(self):
        response = self.client.get(reverse('jobs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find Your")
        self.assertContains(response, "Senior Python Architect")

    def test_job_list_page_loads_and_filters_inactive(self):
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")
        self.assertNotContains(response, "Archived Role")  # Inactive job must not appear

    def test_job_list_search_query(self):
        response = self.client.get(reverse('jobs:job_list'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")

    def test_job_detail_page_loads(self):
        response = self.client.get(reverse('jobs:job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")
        self.assertContains(response, "Acme Tech Innovations")

    def test_inactive_job_returns_404_for_anonymous_user(self):
        response = self.client.get(reverse('jobs:job_detail', args=[self.inactive_job.id]))
        self.assertEqual(response.status_code, 404)

    # 2. Authentication Flow
    def test_candidate_registration(self):
        response = self.client.post(reverse('jobs:register'), {
            'username': 'new_candidate',
            'full_name': 'Bob Smith',
            'email': 'bob@example.com',
            'password': 'StrongPassword2026!',
            'confirm_password': 'StrongPassword2026!',
            'phone': '+1 (555) 999-8888',
            'portfolio_url': 'https://github.com/bob',
            'skills': 'JavaScript, React, Node'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='new_candidate').exists())
        self.assertTrue(Candidate.objects.filter(email='bob@example.com').exists())

    def test_candidate_login_and_logout(self):
        login_res = self.client.post(reverse('jobs:login'), {
            'username': 'candidate_user',
            'password': 'SecurePassword123!'
        }, follow=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_res.context['user'].is_authenticated)

        logout_res = self.client.get(reverse('jobs:logout'), follow=True)
        self.assertEqual(logout_res.status_code, 200)
        self.assertFalse(logout_res.context['user'].is_authenticated)

    # 3. Application Submission & Duplicate Prevention
    def test_apply_job_flow(self):
        self.client.login(username='candidate_user', password='SecurePassword123!')
        response = self.client.post(reverse('jobs:apply_job', args=[self.job.id]), {
            'full_name': 'Alice Candidate',
            'email': 'candidate@example.com',
            'phone': '+1 (555) 123-4567',
            'portfolio_url': 'https://alice.dev',
            'cover_letter': 'I am thrilled to apply for the Senior Python Architect role at Acme.'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(JobApplication.objects.filter(job=self.job, candidate=self.candidate).exists())

    def test_duplicate_application_prevention(self):
        # Create initial application
        JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="First valid submission",
            status="Applied"
        )

        # Database constraint check (wrapped in atomic transaction to prevent breaking test block)
        from django.db import transaction
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                JobApplication.objects.create(
                    job=self.job,
                    candidate=self.candidate,
                    cover_letter="Duplicate attempt",
                    status="Applied"
                )

        # View-level prevention check
        self.client.login(username='candidate_user', password='SecurePassword123!')
        post_res = self.client.post(reverse('jobs:apply_job', args=[self.job.id]), {
            'full_name': 'Alice Candidate',
            'email': 'candidate@example.com',
            'cover_letter': 'Second duplicate attempt via form.'
        }, follow=True)

        self.assertEqual(JobApplication.objects.filter(job=self.job, candidate=self.candidate).count(), 1)
        self.assertContains(post_res, "already applied")

    # 4. Candidate Profile & Applications Access
    def test_candidate_profile_access(self):
        self.client.login(username='candidate_user', password='SecurePassword123!')
        response = self.client.get(reverse('jobs:candidate_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Candidate")

        # Update profile
        update_res = self.client.post(reverse('jobs:candidate_profile'), {
            'full_name': 'Alice Candidate Updated',
            'email': 'candidate@example.com',
            'phone': '+1 (555) 777-8888',
            'portfolio_url': 'https://alice-portfolio.dev',
            'skills': 'Python, Django, AWS, Docker'
        }, follow=True)
        self.assertEqual(update_res.status_code, 200)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.full_name, 'Alice Candidate Updated')

    # 5. Recruiter & ATS Permissions Check
    def test_non_staff_cannot_access_recruiter_dashboard(self):
        # Anonymous user gets redirected
        anon_res = self.client.get(reverse('jobs:recruiter_dashboard'))
        self.assertEqual(anon_res.status_code, 302)

        # Ordinary candidate user gets 403 Forbidden
        self.client.login(username='candidate_user', password='SecurePassword123!')
        forbidden_res = self.client.get(reverse('jobs:recruiter_dashboard'))
        self.assertEqual(forbidden_res.status_code, 403)

    def test_staff_can_access_recruiter_dashboard_and_update_status(self):
        # Create application for testing
        app = JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="Testing recruiter review",
            status="Applied"
        )

        self.client.login(username='recruiter_staff', password='StaffPassword123!')
        dash_res = self.client.get(reverse('jobs:recruiter_dashboard'))
        self.assertEqual(dash_res.status_code, 200)
        self.assertContains(dash_res, "Applicant Tracking System")

        # Recruiter updates status
        status_res = self.client.post(
            reverse('jobs:update_application_status', args=[app.id]),
            {'status': 'Shortlisted'},
            follow=True
        )
        self.assertEqual(status_res.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Shortlisted')

    def test_staff_can_manage_and_toggle_job(self):
        self.client.login(username='recruiter_staff', password='StaffPassword123!')
        manage_res = self.client.get(reverse('jobs:manage_jobs'))
        self.assertEqual(manage_res.status_code, 200)

        # Toggle job active to False
        toggle_res = self.client.post(reverse('jobs:toggle_job_active', args=[self.job.id]), follow=True)
        self.assertEqual(toggle_res.status_code, 200)
        self.job.refresh_from_db()
        self.assertFalse(self.job.active)
