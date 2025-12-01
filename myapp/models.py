from django.db import models
from django.utils import timezone
from datetime import timedelta

# Choices for Internship Categories
CATEGORY_CHOICES = [
    ('Software', 'Software Development'),
    ('Marketing', 'Marketing'),
    ('Design', 'Design'),
    ('Finance', 'Finance'),
    ('HR', 'Human Resources'),
    ('Engineering', 'Engineering'),
    ('Other', 'Other'),
]

# Student Model
class Register(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    degree = models.CharField(max_length=100)
    graduation_year = models.CharField(max_length=100)
    GPA = models.CharField(max_length=100)
    Upload_Resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    Bio = models.TextField(max_length=500)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    rights = models.CharField(max_length=100, default='User')

    def __str__(self):
        return self.name

# Employer Model
class Employer(models.Model):
    company_name = models.CharField(max_length=100)
    company_website = models.CharField(max_length=100)
    company_size = models.CharField(max_length=100)
    company_address = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    rights = models.CharField(max_length=100, default='new company', null=True)
    verification_doc = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

# Internship Model
class Internship(models.Model):
    company = models.ForeignKey(Employer, on_delete=models.CASCADE, null=True)
    positionTitle = models.CharField(max_length=100)
    positionDescription = models.TextField()
    department = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Other') # Updated
    internshipType = models.CharField(max_length=100)
    startDate = models.DateField()
    duration = models.CharField(max_length=100)
    stipend = models.CharField(max_length=100)
    positionsAvailable = models.IntegerField(default=1)
    educationLevel = models.CharField(max_length=100)
    Skills = models.CharField(max_length=200)
    preferredSkills = models.CharField(max_length=200)
    applicationDeadline = models.DateField()
    howToApply = models.CharField(max_length=100)
    contactEmail = models.EmailField()
    contactPhone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='Active') # 'Active' or 'Draft'

    def __str__(self):
        return self.positionTitle

# Application Model
class Applications(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, null=True)
    Address = models.CharField(max_length=200)
    TechnicalSkills = models.CharField(max_length=200)
    InternshipType = models.CharField(max_length=100)
    PreferredDuration = models.CharField(max_length=100)
    EarliestStartDate = models.DateField()
    CoverLetter = models.TextField()
    Status = models.CharField(max_length=100, default='pending')

    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} - Application"

# Notification Model
class Notification(models.Model):
    recipient_student = models.ForeignKey(Register, on_delete=models.CASCADE, null=True, blank=True)
    recipient_company = models.ForeignKey(Employer, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification - {self.date}"

# Complaint Model
class Complaint(models.Model):
    student = models.ForeignKey(Register, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Employer, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    filed_by = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='Pending')
    date_filed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint: {self.subject}"

# Review Model
class Review(models.Model):
    student = models.ForeignKey(Register, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.student.name}"

# Project Assignment Model
class ProjectAssignment(models.Model):
    application = models.OneToOneField(Applications, on_delete=models.CASCADE, related_name='project')
    title = models.CharField(max_length=200, default="Internship Project")
    description = models.TextField(blank=True, null=True)
    company_file = models.FileField(upload_to='project_docs/company/', blank=True, null=True)
    student_file = models.FileField(upload_to='project_docs/student/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Project for {self.application.user.name}"

# NEW: Saved Internship Model (Wishlist)
class SavedInternship(models.Model):
    student = models.ForeignKey(Register, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    date_saved = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'internship')

    def __str__(self):
        return f"{self.student.name} saved {self.internship.positionTitle}"