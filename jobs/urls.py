from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public & Candidate pages
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job_view, name='apply_job'),
    path('profile/', views.candidate_profile_view, name='candidate_profile'),
    path('my-applications/', views.my_applications_view, name='my_applications'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Recruiter / ATS Management (Staff Only)
    path('recruiter/', views.recruiter_dashboard_view, name='recruiter_dashboard'),
    path('recruiter/applications/<int:application_id>/', views.application_detail_view, name='application_detail'),
    path('recruiter/applications/<int:application_id>/status/', views.update_application_status_view, name='update_application_status'),
    path('recruiter/jobs/', views.manage_jobs_view, name='manage_jobs'),
    path('recruiter/jobs/create/', views.job_create_view, name='job_create'),
    path('recruiter/jobs/<int:job_id>/edit/', views.job_edit_view, name='job_edit'),
    path('recruiter/jobs/<int:job_id>/toggle/', views.toggle_job_active_view, name='toggle_job_active'),
]
