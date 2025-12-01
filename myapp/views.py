from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .utils import generate_certificate_pdf
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Register, Employer, Internship, Applications, Notification, Complaint, Review, ProjectAssignment, \
    SavedInternship


# --- Public Pages ---
def index(request):
    return render(request, 'indexhome.html')


def registration(request):
    if request.method == "POST":
        data = request.POST
        if Register.objects.filter(email=data['email']).exists():
            return render(request, "registeration.html", {"msg": "Email already registered"})

        Register.objects.create(
            name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=make_password(data['password']),
            university=data['university'],
            major=data['major'],
            phone=data.get('phone') or '',
            location=data.get('location') or '',
            date_of_birth=data.get('date_of_birth') or None,
            degree=data['degree'],
            graduation_year=data['graduation_year'],
            GPA=data.get('GPA') or '0.0',
            Bio=data.get('Bio') or 'No bio provided'
        )
        return redirect('login')
    return render(request, "registeration.html")


def employer_registration(request):
    if request.method == "POST":
        data = request.POST
        if Employer.objects.filter(email=data['email']).exists():
            return render(request, "registeration.html", {"msg": "Email already registered"})

        Employer.objects.create(
            company_name=data['company_name'],
            company_website=data.get('company_website') or "",
            company_size=data['company_size'],
            company_address=data['company_address'],
            industry=data['industry'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=make_password(data['password']),
            verification_doc=request.FILES.get('verification_doc')
        )
        return redirect('login')
    return render(request, "registeration.html")


def login_view(request):
    if request.method == "POST":
        e = request.POST.get("email")
        p = request.POST.get("password")

        student = Register.objects.filter(email=e).first()
        if student and check_password(p, student.password):
            request.session['uid'] = student.id
            request.session['role'] = 'student'
            return redirect('user_dashboard')

        employer = Employer.objects.filter(email=e).first()
        if employer and check_password(p, employer.password):
            if employer.rights == 'Approved':
                request.session['cid'] = employer.id
                request.session['role'] = 'employer'
                return redirect('company_dashboard')
            else:
                return render(request, 'login.html', {"msg": "Account pending approval"})

        if e == "admin@gmail.com" and p == "admin123":
            request.session['role'] = 'admin'
            return redirect('admin_dashboard')

        return render(request, 'login.html', {"msg": "Invalid Credentials"})
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('index')


# --- Student Dashboards ---
def user_dashboard(request):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])

    strength = 0
    if student.name and student.last_name and student.email: strength += 30
    if student.university and student.major and student.degree: strength += 10
    if student.phone: strength += 10
    if student.location: strength += 10
    if student.Bio and student.Bio != 'No bio provided': strength += 10
    if student.Upload_Resume: strength += 20
    if student.profile_picture: strength += 10
    if strength > 100: strength = 100

    return render(request, 'user/userprofile.html', {'reg': student, 'strength': strength})


def profile_view(request):
    return user_dashboard(request)


def user_edit(request):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])

    if request.method == "POST":
        student.name = request.POST.get('firstName')
        student.last_name = request.POST.get('lastName')
        student.phone = request.POST.get('phone')
        student.location = request.POST.get('location')
        student.Bio = request.POST.get('bio')

        if request.FILES.get('profile_picture'):
            student.profile_picture = request.FILES['profile_picture']
        if request.FILES.get('resume'):
            student.Upload_Resume = request.FILES['resume']

        student.save()
        messages.success(request, "Profile Updated Successfully!")
        return redirect('user_dashboard')

    return render(request, 'user/useredit.html', {'reg': student})


def browse_internships(request):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])

    internships = Internship.objects.filter(status='Active').order_by('-id')
    query = request.GET.get('q')
    category = request.GET.get('category')
    location = request.GET.get('location')

    if query:
        internships = internships.filter(Q(positionTitle__icontains=query) | Q(company__company_name__icontains=query))
    if category and category != 'All':
        internships = internships.filter(department__icontains=category)
    if location:
        internships = internships.filter(internshipType__icontains=location)

    applied_ids = list(Applications.objects.filter(user=student).values_list('internship_id', flat=True))
    saved_ids = list(SavedInternship.objects.filter(student=student).values_list('internship_id', flat=True))

    return render(request, 'user/application.html',
                  {'inte': internships, 'applied_ids': applied_ids, 'saved_ids': saved_ids})


def toggle_saved_internship(request, id):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])
    internship = get_object_or_404(Internship, id=id)
    saved_item = SavedInternship.objects.filter(student=student, internship=internship).first()

    if saved_item:
        saved_item.delete()
        messages.success(request, "Removed from saved jobs.")
    else:
        SavedInternship.objects.create(student=student, internship=internship)
        messages.success(request, "Job saved successfully!")
    return redirect('browse_internships')


def my_applications(request):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])
    my_apps = Applications.objects.filter(user=student).order_by('-id')
    return render(request, 'user/my_applications.html', {'apps': my_apps})


def apply_for_internship(request, internship_id):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])
    internship = get_object_or_404(Internship, id=internship_id)

    if request.method == "POST":
        Applications.objects.create(
            user=student,
            internship=internship,
            Address=request.POST.get('address'),
            TechnicalSkills=request.POST.get('skills'),
            InternshipType=request.POST.get('internshipType'),
            PreferredDuration=request.POST.get('duration'),
            EarliestStartDate=request.POST.get('startDate'),
            CoverLetter=request.POST.get('coverletter')
        )
        Notification.objects.create(recipient_student=student,
                                    message=f"Application sent for {internship.positionTitle}.")
        Notification.objects.create(recipient_company=internship.company,
                                    message=f"New applicant: {student.name} for {internship.positionTitle}.")
        return redirect('browse_internships')
    return render(request, 'user/applicationform.html', {'reg': student, 'internship': internship})


# --- Company Dashboards ---
def company_dashboard(request):
    if 'cid' not in request.session: return redirect('login')
    employer = Employer.objects.get(id=request.session['cid'])
    return render(request, 'company/company.html')


def add_internship(request):
    if 'cid' not in request.session: return redirect('login')
    employer = Employer.objects.get(id=request.session['cid'])

    if request.method == "POST":
        d = request.POST
        status_val = 'Draft' if 'save_draft' in request.POST else 'Active'
        Internship.objects.create(
            company=employer, positionTitle=d['positionTitle'], positionDescription=d['positionDescription'],
            department=d['department'], internshipType=d['internshipType'], startDate=d['startDate'],
            duration=d['duration'], stipend=d['stipend'], positionsAvailable=d['positionsAvailable'],
            educationLevel=d.get('educationLevel', 'Any'), Skills=d['skills'],
            preferredSkills=d.get('preferredSkills', ''),
            applicationDeadline=d['applicationDeadline'], howToApply=d['howToApply'], contactEmail=d['contactEmail'],
            contactPhone=d.get('contactPhone', ''), status=status_val
        )
        messages.success(request, "Internship Created!")
        return redirect('company_dashboard')
    return render(request, "company/internship.html")


def manage_internships(request):
    if 'cid' not in request.session: return redirect('login')
    employer = Employer.objects.get(id=request.session['cid'])
    internships = Internship.objects.filter(company=employer)
    return render(request, 'company/internshipmanager.html', {'inte': internships})


def edit_internship(request, id):
    if 'cid' not in request.session: return redirect('login')
    internship = get_object_or_404(Internship, id=id)
    if request.method == "POST":
        d = request.POST
        internship.positionTitle = d['positionTitle']
        # ... (update other fields)
        internship.save()
        return redirect('manage_internships')
    return render(request, "company/internship.html", {'data': internship})


def delete_internship(request, id):
    if 'cid' not in request.session: return redirect('login')
    get_object_or_404(Internship, id=id).delete()
    return redirect('manage_internships')


# REAL-WORLD KANBAN DATA PREP
def company_profile_apps(request):
    if 'cid' not in request.session: return redirect('login')
    employer = Employer.objects.get(id=request.session['cid'])
    apps = Applications.objects.filter(internship__company=employer)

    # Categorize applications for the Kanban board
    kanban = {
        'pending': apps.filter(Status='pending'),
        'interview': apps.filter(Status='Interview Scheduled'),
        'selected': apps.filter(Status='Approved'),
        'rejected': apps.filter(Status='Rejected'),
        'completed': apps.filter(Status='Completed')
    }
    return render(request, 'company/companyprofile.html', {'kanban': kanban})


# UNIFIED STATUS UPDATE VIEW
def update_application_status(request, id, status):
    if 'cid' not in request.session: return redirect('login')
    app = get_object_or_404(Applications, id=id)

    app.Status = status
    msg_student = ""

    if status == 'Approved':
        msg_student = f"Congrats! You have been Selected for {app.internship.positionTitle}."
    elif status == 'Rejected':
        app.rejection_reason = request.POST.get('reason', 'Position closed')
        msg_student = f"Update: Your application for {app.internship.positionTitle} was not selected."
    elif status == 'Interview Scheduled':
        app.interview_date = request.POST.get('date')
        app.interview_link = request.POST.get('link')
        msg_student = f"Interview scheduled for {app.internship.positionTitle}. Check your dashboard."

    app.save()
    if msg_student:
        Notification.objects.create(recipient_student=app.user, message=msg_student)

    messages.success(request, f"Candidate moved to {status}")
    return redirect('company_profile_apps')


# Kept for backward compatibility but redirecting to unified logic logic if needed
def approve_application(request, id):
    return update_application_status(request, id, 'Approved')


def reject_application(request, id):
    return update_application_status(request, id, 'Rejected')


def schedule_interview(request, id):
    return update_application_status(request, id, 'Interview Scheduled')


def mark_completed(request, id):
    if 'cid' not in request.session: return redirect('login')
    app = get_object_or_404(Applications, id=id)
    app.Status = 'Completed'
    if not app.certificate:
        pdf = generate_certificate_pdf(app)
        app.certificate.save(pdf.name, pdf)
    app.save()
    Notification.objects.create(recipient_student=app.user,
                                message=f"Internship Completed: {app.internship.positionTitle}")
    return redirect('company_profile_apps')


# ... (Keep Admin, Complaint, Notification, Project views as they were) ...
# (They are omitted here for brevity but ensure you keep them in your file)
# --- Admin Dashboards ---
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')


def new_company(request):
    companies = Employer.objects.filter(rights='new company')
    return render(request, 'admin/new_company.html', {'com': companies})


def approve_company(request, id):
    Employer.objects.filter(id=id).update(rights='Approved')
    return redirect('new_company')


def reject_company(request, id):
    Employer.objects.filter(id=id).update(rights='Rejected')
    return redirect('new_company')


def company_list(request):
    companies = Employer.objects.filter(rights='Approved')
    return render(request, 'admin/companies.html', {'com': companies})


def file_complaint(request):
    if 'uid' in request.session:
        user_type = 'Student'
        obj = Register.objects.get(id=request.session['uid'])
    elif 'cid' in request.session:
        user_type = 'Employer'
        obj = Employer.objects.get(id=request.session['cid'])
    else:
        return redirect('login')

    if request.method == "POST":
        subject = request.POST.get('subject')
        description = request.POST.get('description')

        c = Complaint(subject=subject, description=description, filed_by=user_type, status='Pending')
        if user_type == 'Student':
            c.student = obj
        else:
            c.company = obj
        c.save()

        messages.success(request, "Complaint submitted. Admin will review it shortly.")
        return redirect('user_dashboard' if user_type == 'Student' else 'company_dashboard')

    return render(request, 'common/file_complaint.html')


def admin_complaints(request):
    if request.session.get('role') != 'admin': return redirect('login')
    complaints = Complaint.objects.all().order_by('-date_filed')
    return render(request, 'admin/admin_complaints.html', {'complaints': complaints})


def resolve_complaint(request, id):
    if request.session.get('role') != 'admin': return redirect('login')
    complaint = get_object_or_404(Complaint, id=id)
    complaint.status = 'Resolved'
    complaint.save()
    messages.success(request, "Dispute marked as resolved.")
    return redirect('admin_complaints')


def my_notifications(request):
    if 'uid' in request.session:
        user = Register.objects.get(id=request.session['uid'])
        notifs = Notification.objects.filter(recipient_student=user).order_by('-date')
    elif 'cid' in request.session:
        company = Employer.objects.get(id=request.session['cid'])
        notifs = Notification.objects.filter(recipient_company=company).order_by('-date')
    else:
        return redirect('login')

    return render(request, 'common/notifications.html', {'notifs': notifs})


def project_workspace(request, id):
    if 'uid' not in request.session and 'cid' not in request.session:
        return redirect('login')

    app = get_object_or_404(Applications, id=id)
    project, created = ProjectAssignment.objects.get_or_create(application=app)
    user_role = 'student' if 'uid' in request.session else 'employer'

    if request.method == "POST":
        if user_role == 'employer':
            project.title = request.POST.get('title')
            project.description = request.POST.get('description')
            if request.FILES.get('company_file'):
                project.company_file = request.FILES['company_file']
            project.save()

            Notification.objects.create(
                recipient_student=app.user,
                message=f"Project Update: {app.internship.company.company_name} has updated the project details."
            )
            messages.success(request, "Project details updated successfully!")

        elif user_role == 'student':
            if request.FILES.get('student_file'):
                project.student_file = request.FILES['student_file']
                project.save()

                Notification.objects.create(
                    recipient_company=app.internship.company,
                    message=f"Project Submission: {app.user.name} has uploaded a new file."
                )
                messages.success(request, "Work submitted successfully!")

        return redirect('project_workspace', id=id)

    return render(request, 'common/project_workspace.html', {'app': app, 'project': project, 'user_role': user_role})


def project_archive(request):
    if 'uid' in request.session:
        student = Register.objects.get(id=request.session['uid'])
        projects = ProjectAssignment.objects.filter(application__user=student).order_by('-created_at')
        role = 'student'
    elif 'cid' in request.session:
        employer = Employer.objects.get(id=request.session['cid'])
        projects = ProjectAssignment.objects.filter(application__internship__company=employer).order_by('-created_at')
        role = 'employer'
    else:
        return redirect('login')

    return render(request, 'common/project_archive.html', {'projects': projects, 'role': role})


def submit_review(request, id):
    if 'uid' not in request.session: return redirect('login')
    student = Register.objects.get(id=request.session['uid'])
    app = get_object_or_404(Applications, id=id, user=student)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            student=student,
            internship=app.internship,
            rating=rating,
            comment=comment
        )

        Notification.objects.create(
            recipient_company=app.internship.company,
            message=f"New Review: {student.name} rated their experience {rating}/5."
        )

        messages.success(request, "Review submitted successfully!")
        return redirect('my_applications')

    return redirect('my_applications')


def admin_send_notification(request):
    if request.session.get('role') != 'admin': return redirect('login')

    if request.method == "POST":
        target = request.POST.get('target')
        message = request.POST.get('message')

        if target == 'students' or target == 'all':
            for s in Register.objects.all():
                Notification.objects.create(recipient_student=s, message=message)

        if target == 'companies' or target == 'all':
            for c in Employer.objects.all():
                Notification.objects.create(recipient_company=c, message=message)

        messages.success(request, "Notification sent successfully!")
        return redirect('admin_dashboard')

    return render(request, 'admin/send_notification.html')