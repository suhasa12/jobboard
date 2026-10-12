"""
URL configuration for jobboard_project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls', namespace='jobs')),
]

# Custom HTTP error handlers
handler403 = 'jobs.views.custom_permission_denied_view'
handler404 = 'jobs.views.custom_page_not_found_view'
