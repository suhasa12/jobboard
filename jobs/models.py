from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    website = models.URLField(max_length=300, blank=True)
    location = models.CharField(max_length=200)
    logo_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Direct link to company logo image"
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    JOB_TYPES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=250)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, default='Full-time')
    required_skills = models.CharField(max_length=300, help_text="Comma-separated skills (e.g., Python, Django, SQL)")
    salary_range = models.CharField(max_length=100, help_text="e.g., $85,000 - $115,000 / year")
    description = models.TextField()
    active = models.BooleanField(default=True)
    posted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    @property
    def skills_list(self):
        if not self.required_skills:
            return []
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=30, blank=True)
    portfolio_url = models.URLField(max_length=300, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated or list of candidate skills")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def skills_list(self):
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    applied_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_date']
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'candidate'],
                name='unique_job_candidate_application'
            )
        ]

    def __str__(self):
        return f"{self.candidate.full_name} -> {self.job.title} ({self.status})"

    @property
    def status_badge_class(self):
        badges = {
            'Applied': 'bg-primary',
            'Under Review': 'bg-warning text-dark',
            'Shortlisted': 'bg-success',
            'Rejected': 'bg-danger',
        }
        return badges.get(self.status, 'bg-secondary')
