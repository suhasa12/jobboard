from django.contrib import admin
from .models import Company, JobPosting, Candidate, JobApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website', 'created_at')
    search_fields = ('name', 'location', 'description')
    list_filter = ('location',)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'salary_range', 'active', 'posted_date')
    list_filter = ('job_type', 'active', 'posted_date', 'company')
    search_fields = ('title', 'required_skills', 'description', 'company__name')
    list_editable = ('active',)
    actions = ['make_active', 'make_inactive']

    @admin.action(description="Mark selected jobs as active")
    def make_active(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Mark selected jobs as inactive")
    def make_inactive(self, request, queryset):
        queryset.update(active=False)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'portfolio_url', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'skills', 'user__username')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'applied_date')
    list_filter = ('status', 'applied_date', 'job__job_type')
    search_fields = ('candidate__full_name', 'candidate__email', 'job__title', 'job__company__name', 'cover_letter')
    list_editable = ('status',)
