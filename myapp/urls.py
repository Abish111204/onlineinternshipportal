from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('submit-review/<int:id>/', views.submit_review, name='submit_review'),
    # Note: Updated to generic status update
    path('update-status/<int:id>/<str:status>/', views.update_application_status, name='update_status'),
    path('schedule-interview/<int:id>/', views.schedule_interview, name='schedule_interview'),
    path('project-workspace/<int:id>/', views.project_workspace, name='project_workspace'),
    path('projects-archive/', views.project_archive, name='project_archive'),

    # Registration & Login
    path('registration/', views.registration, name='register'),
    path('employer-registration/', views.employer_registration, name='employer_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Student URLs
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('user/edit/', views.user_edit, name='user_edit'),
    path('application/', views.browse_internships, name='browse_internships'),
    path('apply/<int:internship_id>/', views.apply_for_internship, name='apply_internship'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('file-complaint/', views.file_complaint, name='file_complaint'),
    path('notifications/', views.my_notifications, name='my_notifications'),
    path('toggle-save/<int:id>/', views.toggle_saved_internship, name='toggle_save'),

    # Company URLs
    path('company/', views.company_dashboard, name='company_dashboard'),
    path('internship/add/', views.add_internship, name='add_internship'),
    path('internship/manage/', views.manage_internships, name='manage_internships'),
    path('internship/delete/<int:id>/', views.delete_internship, name='delete_internship'),
    path('internship/edit/<int:id>/', views.edit_internship, name='edit_internship'),
    path('company/profile/', views.company_profile_apps, name='company_profile_apps'),
    # Legacy routes redirected in logic
    path('approve-application/<int:id>/', views.approve_application, name='approve_app'),
    path('reject-application/<int:id>/', views.reject_application, name='reject_app'),
    path('mark-completed/<int:id>/', views.mark_completed, name='mark_completed'),

    # Admin URLs
    path('adminp/', views.admin_dashboard, name='admin_dashboard'),
    path('adminp/new_company/', views.new_company, name='new_company'),
    path('adminp/approve/<int:id>/', views.approve_company, name='approve_company'),
    path('adminp/reject/<int:id>/', views.reject_company, name='reject_company'),
    path('adminp/companies/', views.company_list, name='company_list'),
    path('adminp/complaints/', views.admin_complaints, name='admin_complaints'),
    path('adminp/resolve/<int:id>/', views.resolve_complaint, name='resolve_complaint'),
    path('adminp/notify/', views.admin_send_notification, name='admin_send_notification'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)