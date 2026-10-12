from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed

from .models import Company, JobPosting, Candidate, JobApplication
from .forms import (
    CandidateRegistrationForm,
    CandidateLoginForm,
    CandidateProfileForm,
    JobApplicationForm,
    JobPostingForm,
    ApplicationStatusForm,
    CompanyForm,
)


def staff_required(view_func):
    """Decorator to enforce that the user is authenticated and is a staff member."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with recruiter credentials to access this page.")
            return redirect(f"/login/?next={request.path}")
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to access the recruiter portal.")
        return view_func(request, *args, **kwargs)
    return wrapper


def home_view(request):
    """Landing page with hero, search, statistics, and featured jobs."""
    featured_jobs = JobPosting.objects.filter(active=True).select_related('company')[:6]
    
    context = {
        'featured_jobs': featured_jobs,
        'total_jobs': JobPosting.objects.filter(active=True).count(),
        'total_companies': Company.objects.count(),
        'total_applications': JobApplication.objects.count(),
        'total_candidates': Candidate.objects.count(),
    }
    return render(request, 'jobs/home.html', context)


def job_list_view(request):
    """Job listing page with server-side filters and client-side dynamic search."""
    jobs_queryset = JobPosting.objects.filter(active=True).select_related('company')

    # Server-side query parameter filtering
    query = request.GET.get('q', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    location = request.GET.get('location', '').strip()
    skill_filter = request.GET.get('skill', '').strip()

    if query:
        jobs_queryset = jobs_queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company__name__icontains=query) |
            Q(required_skills__icontains=query)
        )

    if job_type:
        jobs_queryset = jobs_queryset.filter(job_type__iexact=job_type)

    if location:
        jobs_queryset = jobs_queryset.filter(company__location__icontains=location)

    if skill_filter:
        jobs_queryset = jobs_queryset.filter(required_skills__icontains=skill_filter)

    # Collect unique filters for UI dropdowns and badges
    all_active_jobs = JobPosting.objects.filter(active=True).select_related('company')
    available_job_types = JobPosting.JOB_TYPES
    locations = sorted(set(j.company.location for j in all_active_jobs if j.company.location))
    
    # Collect top skills
    all_skills = set()
    for j in all_active_jobs:
        for s in j.skills_list:
            if s:
                all_skills.add(s)
    popular_skills = sorted(list(all_skills))[:12]

    context = {
        'jobs': jobs_queryset,
        'job_count': jobs_queryset.count(),
        'search_query': query,
        'selected_job_type': job_type,
        'selected_location': location,
        'selected_skill': skill_filter,
        'job_types': available_job_types,
        'locations': locations,
        'popular_skills': popular_skills,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, job_id):
    """Displays job details, company info, and handles application state."""
    job = get_object_or_404(JobPosting.objects.select_related('company'), id=job_id)
    if not job.active and not request.user.is_staff:
        # Non-staff users cannot view inactive jobs
        return render(request, 'jobs/404.html', status=404)

    existing_application = None
    candidate = None
    application_form = None

    if request.user.is_authenticated:
        try:
            candidate = request.user.candidate_profile
        except Candidate.DoesNotExist:
            candidate = None

        if candidate:
            existing_application = JobApplication.objects.filter(job=job, candidate=candidate).first()

        # Pre-fill application form with candidate information
        initial_data = {}
        if candidate:
            initial_data = {
                'full_name': candidate.full_name or request.user.get_full_name() or request.user.username,
                'email': candidate.email or request.user.email,
                'phone': candidate.phone,
                'portfolio_url': candidate.portfolio_url,
            }
        else:
            initial_data = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        application_form = JobApplicationForm(initial=initial_data)

    context = {
        'job': job,
        'existing_application': existing_application,
        'application_form': application_form,
    }
    return render(request, 'jobs/job_detail.html', context)


def apply_job_view(request, job_id):
    """Handles candidate application submission (both standalone page and modal submission)."""
    job = get_object_or_404(JobPosting.objects.select_related('company'), id=job_id)

    if not job.active:
        messages.error(request, "This job posting is no longer active.")
        return redirect('jobs:job_list')

    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to apply for this position.")
        return redirect(f"/login/?next=/jobs/{job_id}/apply/")

    # Retrieve or create candidate profile for authenticated user
    candidate, _ = Candidate.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
    )

    # Check for existing application (prevent duplicates)
    existing_application = JobApplication.objects.filter(job=job, candidate=candidate).first()
    if existing_application:
        messages.info(
            request,
            f"You have already applied for '{job.title}'. Current status: {existing_application.status}."
        )
        return redirect('jobs:job_detail', job_id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            # Update candidate profile with latest verified details
            candidate.full_name = form.cleaned_data['full_name']
            candidate.email = form.cleaned_data['email']
            candidate.phone = form.cleaned_data.get('phone', '')
            candidate.portfolio_url = form.cleaned_data.get('portfolio_url', '')
            candidate.save()

            # Create application
            try:
                application = JobApplication.objects.create(
                    job=job,
                    candidate=candidate,
                    cover_letter=form.cleaned_data['cover_letter'],
                    status='Applied'
                )
                messages.success(
                    request,
                    f"Congratulations! Your application for '{job.title}' at {job.company.name} has been submitted successfully."
                )
                return redirect('jobs:my_applications')
            except Exception:
                messages.error(request, "An application for this role has already been submitted.")
                return redirect('jobs:job_detail', job_id=job.id)
        else:
            messages.error(request, "Please correct the errors in the application form below.")
    else:
        initial_data = {
            'full_name': candidate.full_name or request.user.get_full_name() or request.user.username,
            'email': candidate.email or request.user.email,
            'phone': candidate.phone,
            'portfolio_url': candidate.portfolio_url,
        }
        form = JobApplicationForm(initial=initial_data)

    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'jobs/apply.html', context)


def register_view(request):
    """Candidate registration with server-side validation and automatic login."""
    if request.user.is_authenticated:
        return redirect('jobs:home')

    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user, candidate = form.save()
            auth_login(request, user)
            messages.success(
                request,
                f"Welcome to JobBoard, {candidate.full_name}! Your profile has been created."
            )
            return redirect('jobs:job_list')
        else:
            messages.error(request, "Please correct the errors below to complete registration.")
    else:
        form = CandidateRegistrationForm()

    return render(request, 'jobs/register.html', {'form': form})


def login_view(request):
    """User authentication view supporting candidates and recruiters."""
    if request.user.is_authenticated:
        return redirect('jobs:home')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = CandidateLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                
                # Check redirect target
                redirect_target = request.POST.get('next', '') or next_url
                if redirect_target:
                    return redirect(redirect_target)
                if user.is_staff:
                    return redirect('jobs:recruiter_dashboard')
                return redirect('jobs:home')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CandidateLoginForm()

    return render(request, 'jobs/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """Logs out the active user."""
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('jobs:home')


@login_required
def candidate_profile_view(request):
    """Candidate profile view and edit, restricted to candidate's own profile."""
    candidate, _ = Candidate.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
    )

    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('jobs:candidate_profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = CandidateProfileForm(instance=candidate)

    context = {
        'candidate': candidate,
        'form': form,
    }
    return render(request, 'jobs/candidate_profile.html', context)


@login_required
def my_applications_view(request):
    """Displays applications submitted by the logged-in candidate."""
    try:
        candidate = request.user.candidate_profile
        applications = JobApplication.objects.filter(candidate=candidate).select_related('job', 'job__company').order_by('-applied_date')
    except Candidate.DoesNotExist:
        applications = []

    context = {
        'applications': applications,
        'count': len(applications),
    }
    return render(request, 'jobs/my_applications.html', context)


# ==============================================================================
# RECRUITER & ATS MANAGEMENT VIEWS (Restricted to Staff)
# ==============================================================================

@staff_required
def recruiter_dashboard_view(request):
    """Recruiter ATS Dashboard with status metrics, filterable applications, and actions."""
    status_filter = request.GET.get('status', '').strip()
    search_query = request.GET.get('q', '').strip()

    applications = JobApplication.objects.select_related('job', 'job__company', 'candidate').order_by('-applied_date')

    if status_filter:
        applications = applications.filter(status=status_filter)

    if search_query:
        applications = applications.filter(
            Q(candidate__full_name__icontains=search_query) |
            Q(candidate__email__icontains=search_query) |
            Q(job__title__icontains=search_query) |
            Q(job__company__name__icontains=search_query)
        )

    # Calculate status counts
    all_apps = JobApplication.objects.all()
    stats = {
        'total': all_apps.count(),
        'applied': all_apps.filter(status='Applied').count(),
        'under_review': all_apps.filter(status='Under Review').count(),
        'shortlisted': all_apps.filter(status='Shortlisted').count(),
        'rejected': all_apps.filter(status='Rejected').count(),
        'total_jobs': JobPosting.objects.count(),
        'active_jobs': JobPosting.objects.filter(active=True).count(),
    }

    context = {
        'applications': applications,
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    return render(request, 'jobs/recruiter_dashboard.html', context)


@staff_required
def update_application_status_view(request, application_id):
    """POST-only view for recruiters to update candidate application status."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    application = get_object_or_404(JobApplication, id=application_id)
    new_status = request.POST.get('status', '').strip()

    valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
    if new_status in valid_statuses:
        application.status = new_status
        application.save()
        messages.success(
            request,
            f"Updated status for {application.candidate.full_name} to '{new_status}'."
        )
    else:
        messages.error(request, "Invalid status choice selected.")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'jobs:recruiter_dashboard'
    return redirect(next_url)


@staff_required
def application_detail_view(request, application_id):
    """Detailed view of an applicant's submission for recruiter evaluation."""
    application = get_object_or_404(
        JobApplication.objects.select_related('candidate', 'job', 'job__company'),
        id=application_id
    )

    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f"Application status updated to '{application.status}'.")
            return redirect('jobs:application_detail', application_id=application.id)
    else:
        form = ApplicationStatusForm(instance=application)

    context = {
        'application': application,
        'form': form,
    }
    return render(request, 'jobs/application_detail.html', context)


@staff_required
def manage_jobs_view(request):
    """Recruiter page to manage, view, edit, activate/deactivate job postings."""
    jobs = (
        JobPosting.objects
        .select_related('company')
        .annotate(applicant_count=Count('applications'))
        .order_by('-posted_date')
    )

    context = {
        'jobs': jobs,
    }
    return render(request, 'jobs/manage_jobs.html', context)


@staff_required
def job_create_view(request):
    """Allows staff recruiters to post a new job."""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job posting '{job.title}' created successfully!")
            return redirect('jobs:manage_jobs')
        else:
            messages.error(request, "Please correct the errors in the job form.")
    else:
        form = JobPostingForm()

    context = {
        'form': form,
        'action_title': 'Post a New Job',
        'button_text': 'Publish Job Posting',
    }
    return render(request, 'jobs/job_form.html', context)


@staff_required
def job_edit_view(request, job_id):
    """Allows staff recruiters to edit an existing job posting."""
    job = get_object_or_404(JobPosting, id=job_id)

    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job posting '{job.title}' updated successfully!")
            return redirect('jobs:manage_jobs')
        else:
            messages.error(request, "Please correct the errors in the job form.")
    else:
        form = JobPostingForm(instance=job)

    context = {
        'form': form,
        'job': job,
        'action_title': f"Edit Job: {job.title}",
        'button_text': 'Save Changes',
    }
    return render(request, 'jobs/job_form.html', context)


@staff_required
def toggle_job_active_view(request, job_id):
    """POST-only view to activate or deactivate a job posting."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    job = get_object_or_404(JobPosting, id=job_id)
    job.active = not job.active
    job.save()

    status_str = "Active" if job.active else "Inactive"
    messages.success(request, f"Job '{job.title}' is now {status_str}.")
    return redirect('jobs:manage_jobs')


# Error handlers
def custom_permission_denied_view(request, exception=None):
    """Custom 403 Forbidden handler."""
    return render(request, 'jobs/403.html', status=403)


def custom_page_not_found_view(request, exception=None):
    """Custom 404 Not Found handler."""
    return render(request, 'jobs/404.html', status=404)
