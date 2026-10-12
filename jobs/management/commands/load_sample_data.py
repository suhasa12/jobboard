from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Company, JobPosting, Candidate, JobApplication


class Command(BaseCommand):
    help = "Loads safe, idempotent demonstration data for the JobBoard ATS platform."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demonstration data..."))

        # -------------------------------------------------------------
        # 1. Companies (5 Sample Companies)
        # -------------------------------------------------------------
        companies_data = [
            {
                "name": "CloudScale Systems",
                "location": "San Francisco, CA / Remote",
                "website": "https://cloudscale.example.com",
                "logo_url": "https://images.unsplash.com/photo-1542744094-3a31f272c490?w=128&auto=format&fit=crop&q=80",
                "description": "Next-generation distributed cloud infrastructure and observability platform serving Fortune 500 engineering teams.",
            },
            {
                "name": "DataPulse Analytics",
                "location": "New York, NY",
                "website": "https://datapulse.example.com",
                "logo_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=128&auto=format&fit=crop&q=80",
                "description": "Real-time streaming analytics engine and machine learning data pipelines for high-frequency fintech systems.",
            },
            {
                "name": "Apex Fintech Labs",
                "location": "Austin, TX / Hybrid",
                "website": "https://apexfintech.example.com",
                "logo_url": "https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=128&auto=format&fit=crop&q=80",
                "description": "Building modern banking APIs, regulatory compliance automation, and distributed payment rails.",
            },
            {
                "name": "Nexus Health Tech",
                "location": "Boston, MA",
                "website": "https://nexushealth.example.com",
                "logo_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=128&auto=format&fit=crop&q=80",
                "description": "HIPAA-compliant telemedicine platforms and clinical workflow orchestration for health systems globally.",
            },
            {
                "name": "Quantum Cyber Solutions",
                "location": "Remote / Global",
                "website": "https://quantumcyber.example.com",
                "logo_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=128&auto=format&fit=crop&q=80",
                "description": "Zero-trust identity enforcement, cloud posture governance, and incident mitigation architecture.",
            },
        ]

        companies = {}
        for cdata in companies_data:
            company, created = Company.objects.get_or_create(
                name=cdata["name"],
                defaults={
                    "location": cdata["location"],
                    "website": cdata["website"],
                    "logo_url": cdata["logo_url"],
                    "description": cdata["description"],
                }
            )
            companies[company.name] = company
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created company: {company.name}"))
            else:
                self.stdout.write(f"  Existing company: {company.name}")

        # -------------------------------------------------------------
        # 2. Job Postings (16 Diverse Postings across all job types)
        # -------------------------------------------------------------
        jobs_data = [
            {
                "company": companies["CloudScale Systems"],
                "title": "Senior Django Backend Architect",
                "job_type": "Full-time",
                "required_skills": "Python, Django, PostgreSQL, Celery, Redis, Docker",
                "salary_range": "$140,000 - $175,000 / year",
                "description": (
                    "We are seeking an experienced Backend Architect to lead the design of our core REST APIs "
                    "and microservices in Django 5. You will optimize database queries, architect scalable queuing "
                    "with Celery and Redis, and work directly with our platform infrastructure team."
                ),
                "active": True,
            },
            {
                "company": companies["CloudScale Systems"],
                "title": "Cloud DevOps & Kubernetes Engineer",
                "job_type": "Full-time",
                "required_skills": "Kubernetes, Terraform, AWS, Docker, CI/CD, Python",
                "salary_range": "$130,000 - $160,000 / year",
                "description": (
                    "Manage multi-region Kubernetes clusters on AWS, write infrastructure-as-code using Terraform, "
                    "and maintain automated deployment pipelines with zero-downtime rolling updates."
                ),
                "active": True,
            },
            {
                "company": companies["CloudScale Systems"],
                "title": "Site Reliability Engineering (SRE) Intern",
                "job_type": "Internship",
                "required_skills": "Python, Linux, Prometheus, Grafana, Docker",
                "salary_range": "$35 - $45 / hour",
                "description": (
                    "Summer internship opportunity for students passionate about infrastructure reliability. "
                    "You will build synthetic monitoring probes, analyze system telemetry, and automate incident alerting."
                ),
                "active": True,
            },
            {
                "company": companies["DataPulse Analytics"],
                "title": "Lead Python Data Engineer",
                "job_type": "Full-time",
                "required_skills": "Python, Apache Kafka, Spark, SQL, Airflow",
                "salary_range": "$145,000 - $180,000 / year",
                "description": (
                    "Own our high-throughput data ingestion pipelines processing millions of events per second. "
                    "Build streaming transformations using Kafka and Spark, and ensure data lake catalog hygiene."
                ),
                "active": True,
            },
            {
                "company": companies["DataPulse Analytics"],
                "title": "Frontend UI/UX Specialist",
                "job_type": "Contract",
                "required_skills": "JavaScript, React, Bootstrap 5, CSS3, HTML5, TypeScript",
                "salary_range": "$75 - $95 / hour",
                "description": (
                    "A 6-month contract role building responsive, high-density data analytics dashboards. "
                    "Implement dynamic chart visualizations, accessible data tables, and cohesive design tokens."
                ),
                "active": True,
            },
            {
                "company": companies["DataPulse Analytics"],
                "title": "Machine Learning Research Associate",
                "job_type": "Full-time",
                "required_skills": "Python, PyTorch, Scikit-learn, SQL, MLOps",
                "salary_range": "$125,000 - $155,000 / year",
                "description": (
                    "Collaborate with PhD researchers to productize predictive models for anomaly detection. "
                    "Evaluate model drift, benchmark inference latency, and deploy models using containerized endpoints."
                ),
                "active": True,
            },
            {
                "company": companies["Apex Fintech Labs"],
                "title": "Full-Stack Web Developer",
                "job_type": "Full-time",
                "required_skills": "Python, Django, JavaScript, Bootstrap, REST APIs, SQLite",
                "salary_range": "$110,000 - $135,000 / year",
                "description": (
                    "Deliver candidate and customer-facing web applications. Implement server-rendered Django templates, "
                    "integrate client-side enhancements using modern JavaScript, and ensure rigorous CSRF and auth controls."
                ),
                "active": True,
            },
            {
                "company": companies["Apex Fintech Labs"],
                "title": "Security & Compliance Analyst",
                "job_type": "Part-time",
                "required_skills": "SOC2, PCI-DSS, Cyber Security, Audit, Risk Assessment",
                "salary_range": "$50 - $70 / hour",
                "description": (
                    "Part-time role (20 hrs/week) auditing access controls, vulnerability scans, and regulatory compliance "
                    "checklists for our banking partner integrations."
                ),
                "active": True,
            },
            {
                "company": companies["Apex Fintech Labs"],
                "title": "Software Engineering Intern - Web Apps",
                "job_type": "Internship",
                "required_skills": "Python, HTML5, CSS3, JavaScript, Git",
                "salary_range": "$30 - $40 / hour",
                "description": (
                    "Mentorship-driven internship working on internal recruiter tools and applicant pipelines. "
                    "Gain hands-on experience with Django ORM, version control workflows, and unit testing."
                ),
                "active": True,
            },
            {
                "company": companies["Nexus Health Tech"],
                "title": "Django API & Integrations Engineer",
                "job_type": "Full-time",
                "required_skills": "Python, Django, FHIR, REST APIs, PostgreSQL, OAuth2",
                "salary_range": "$120,000 - $150,000 / year",
                "description": (
                    "Integrate hospital electronic health records (EHR) with our telehealth suite. "
                    "Enforce strict HIPAA data sanitization, handle webhooks, and build robust error handling."
                ),
                "active": True,
            },
            {
                "company": companies["Nexus Health Tech"],
                "title": "Product Designer (UI/UX)",
                "job_type": "Full-time",
                "required_skills": "Figma, User Research, Design Systems, HTML5, CSS3",
                "salary_range": "$105,000 - $130,000 / year",
                "description": (
                    "Design intuitive, human-centered interfaces for doctors and patients. "
                    "Conduct usability tests, create wireframes, and maintain accessible component design libraries."
                ),
                "active": True,
            },
            {
                "company": companies["Nexus Health Tech"],
                "title": "Technical Writer & Documentation Specialist",
                "job_type": "Contract",
                "required_skills": "Technical Writing, API Documentation, Markdown, Git",
                "salary_range": "$45 - $60 / hour",
                "description": (
                    "Produce comprehensive API guides, developer onboarding portals, and integration tutorials "
                    "for third-party health app developers."
                ),
                "active": True,
            },
            {
                "company": companies["Quantum Cyber Solutions"],
                "title": "Principal Security Operations Engineer",
                "job_type": "Full-time",
                "required_skills": "Python, SIEM, Incident Response, Network Security, Zero-Trust",
                "salary_range": "$160,000 - $195,000 / year",
                "description": (
                    "Lead defensive engineering initiatives. Write automated detection rules in Python, orchestrate "
                    "incident response playbooks, and conduct periodic penetration testing reviews."
                ),
                "active": True,
            },
            {
                "company": companies["Quantum Cyber Solutions"],
                "title": "Systems Integration Contractor",
                "job_type": "Contract",
                "required_skills": "Linux, Bash, Python, Ansible, Docker",
                "salary_range": "$80 - $100 / hour",
                "description": (
                    "Contract role deploying security agents across heterogeneous Linux enterprise environments. "
                    "Build idempotent Ansible configuration playbooks and diagnose connection bottlenecks."
                ),
                "active": True,
            },
            {
                "company": companies["Quantum Cyber Solutions"],
                "title": "Cybersecurity Graduate Intern",
                "job_type": "Internship",
                "required_skills": "Python, Network Fundamentals, Wireshark, Linux",
                "salary_range": "$32 - $42 / hour",
                "description": (
                    "Exciting internship analyzing threat intelligence feeds and malware sandbox outputs. "
                    "Work directly alongside veteran threat hunters."
                ),
                "active": True,
            },
            {
                "company": companies["Quantum Cyber Solutions"],
                "title": "QA Automation & Test Engineer",
                "job_type": "Part-time",
                "required_skills": "Python, PyTest, Selenium, CI/CD, Git",
                "salary_range": "$50 - $65 / hour",
                "description": (
                    "Flexible 25 hrs/week schedule writing automated end-to-end regression tests "
                    "for our customer portal and dashboard features."
                ),
                "active": True,
            },
        ]

        created_jobs = []
        for jdata in jobs_data:
            job, created = JobPosting.objects.get_or_create(
                company=jdata["company"],
                title=jdata["title"],
                defaults={
                    "job_type": jdata["job_type"],
                    "required_skills": jdata["required_skills"],
                    "salary_range": jdata["salary_range"],
                    "description": jdata["description"],
                    "active": jdata["active"],
                }
            )
            created_jobs.append(job)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created job: {job.title}"))

        # -------------------------------------------------------------
        # 3. Demonstration Candidates (Safe setup with unusable passwords)
        # -------------------------------------------------------------
        candidates_data = [
            {
                "username": "alex.morgan",
                "email": "alex.morgan@example.com",
                "first_name": "Alex",
                "last_name": "Morgan",
                "phone": "+1 (555) 234-5678",
                "portfolio_url": "https://github.com/alexmorgan-dev",
                "skills": "Python, Django, PostgreSQL, Docker, AWS, Celery",
            },
            {
                "username": "sarah.connor",
                "email": "sarah.connor@example.com",
                "first_name": "Sarah",
                "last_name": "Connor",
                "phone": "+1 (555) 876-5432",
                "portfolio_url": "https://sarahconnor.tech",
                "skills": "JavaScript, React, Bootstrap 5, CSS3, HTML5, TypeScript",
            },
            {
                "username": "david.kim",
                "email": "david.kim@example.com",
                "first_name": "David",
                "last_name": "Kim",
                "phone": "+1 (555) 345-6789",
                "portfolio_url": "https://davidkim-sre.io",
                "skills": "Kubernetes, Terraform, AWS, Linux, Prometheus, Grafana",
            },
        ]

        sample_candidates = []
        for cdata in candidates_data:
            user, u_created = User.objects.get_or_create(
                username=cdata["username"],
                defaults={
                    "email": cdata["email"],
                    "first_name": cdata["first_name"],
                    "last_name": cdata["last_name"],
                }
            )
            if u_created:
                # Set a safe random/unusable password or placeholder for demo users
                user.set_password("CandidateDemoPass2026!")
                user.save()

            candidate, cand_created = Candidate.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": f"{cdata['first_name']} {cdata['last_name']}",
                    "email": cdata["email"],
                    "phone": cdata["phone"],
                    "portfolio_url": cdata["portfolio_url"],
                    "skills": cdata["skills"],
                }
            )
            sample_candidates.append(candidate)
            if cand_created:
                self.stdout.write(self.style.SUCCESS(f"  Created candidate: {candidate.full_name}"))

        # -------------------------------------------------------------
        # 4. Demonstration Job Applications (Diverse Statuses)
        # -------------------------------------------------------------
        if len(sample_candidates) >= 3 and len(created_jobs) >= 4:
            apps_data = [
                {
                    "job": created_jobs[0],  # Senior Django Backend Architect
                    "candidate": sample_candidates[0],  # Alex Morgan
                    "status": "Shortlisted",
                    "cover_letter": (
                        "Dear Hiring Team,\n\n"
                        "I am writing to express my strong enthusiasm for the Senior Django Backend Architect position. "
                        "Over the last 6 years, I have architected high-performance Django APIs supporting millions of requests. "
                        "I am particularly drawn to CloudScale's mission of distributed observability. "
                        "I look forward to discussing how my experience with PostgreSQL optimization and Celery can accelerate your milestones."
                    ),
                },
                {
                    "job": created_jobs[4],  # Frontend UI/UX Specialist
                    "candidate": sample_candidates[1],  # Sarah Connor
                    "status": "Under Review",
                    "cover_letter": (
                        "Hello DataPulse Team,\n\n"
                        "Having crafted accessible and responsive UI systems in Bootstrap 5 and React for enterprise clients, "
                        "I was excited to see this opening. I specialize in designing streamlined data analytics views that minimize cognitive load. "
                        "My portfolio includes recent dashboard overhauls that improved user engagement by 40%."
                    ),
                },
                {
                    "job": created_jobs[1],  # Cloud DevOps & Kubernetes Engineer
                    "candidate": sample_candidates[2],  # David Kim
                    "status": "Applied",
                    "cover_letter": (
                        "Hi,\n\n"
                        "I have spent the past 4 years managing production Kubernetes clusters and authoring modular Terraform configurations. "
                        "Your cloud infrastructure requirements align directly with my hands-on background in zero-downtime CI/CD deployments."
                    ),
                },
                {
                    "job": created_jobs[6],  # Full-Stack Web Developer at Apex
                    "candidate": sample_candidates[0],  # Alex Morgan
                    "status": "Rejected",
                    "cover_letter": (
                        "Greetings,\n\n"
                        "Please accept my application for the Full-Stack Developer position. I possess strong backend expertise and "
                        "familiarity with financial compliance workflows."
                    ),
                },
            ]

            for adata in apps_data:
                app, created = JobApplication.objects.get_or_create(
                    job=adata["job"],
                    candidate=adata["candidate"],
                    defaults={
                        "status": adata["status"],
                        "cover_letter": adata["cover_letter"],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created application: {app.candidate.full_name} -> {app.job.title} ({app.status})"))

        self.stdout.write(self.style.SUCCESS("\nDemonstration data loaded successfully!"))
