import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Company, JobPosting, Candidate, JobApplication


class CandidateRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. jdoe'})
    )
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Jane Doe'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jane@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Minimum 8 characters'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-type password'}),
        min_length=8
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'})
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/janedoe'})
    )
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Python, Django, React, PostgreSQL'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        # Split full name into first and last name if possible
        name_parts = data['full_name'].strip().split(' ', 1)
        user.first_name = name_parts[0]
        if len(name_parts) > 1:
            user.last_name = name_parts[1]
        user.save()

        candidate = Candidate.objects.create(
            user=user,
            full_name=data['full_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            portfolio_url=data.get('portfolio_url', ''),
            skills=data.get('skills', '')
        )
        return user, candidate


class CandidateLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['full_name', 'email', 'phone', 'portfolio_url', 'skills']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Django, AWS...'}),
        }

    def save(self, commit=True):
        candidate = super().save(commit=commit)
        if commit:
            # Sync email with linked User model
            candidate.user.email = candidate.email
            candidate.user.save()
        return candidate


class JobApplicationForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Portfolio / GitHub URL'})
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Tell the hiring team why you are an ideal fit for this role...'
        })
    )

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter', '').strip()
        if len(cover_letter) < 20:
            raise ValidationError("Please provide a cover letter with at least 20 characters explaining your interest.")
        return cover_letter


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'company', 'job_type', 'required_skills', 'salary_range', 'description', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Django Developer'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, Django, PostgreSQL, Docker'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $90,000 - $120,000 / year'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe job duties, requirements, benefits...'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'location', 'logo_url', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://company.com'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country or Remote'}),
            'logo_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://.../logo.png'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
