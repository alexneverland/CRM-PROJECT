# crm_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from django.urls import reverse_lazy 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Το login παραμένει ως έχει με auth_views.LoginView αν λειτουργεί σωστά
    path('accounts/login/', 
         # auth_views.LoginView.as_view(template_name='registration/login.html'), # Αν χρησιμοποιείς το auth_views
         # Εναλλακτικά, αν έχεις custom login view:
         # core_views.your_custom_login_view, # Παράδειγμα
         # Για τώρα, ας υποθέσουμε ότι το login σου είναι ΟΚ.
         # Χρειάζεται η εισαγωγή: from django.contrib.auth import views as auth_views
         auth_views.LoginView.as_view(template_name='registration/login.html'), 
         name='login'),

    path('accounts/logout/', 
         core_views.custom_logout_view, # <<< ΑΛΛΑΓΗ ΕΔΩ: Χρήση της δικής μας view
         name='logout'),
     path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html', # Template για το email
             subject_template_name='registration/password_reset_subject.txt', # Template για το θέμα του email
             success_url=reverse_lazy('password_reset_done') # Χρησιμοποιούμε reverse_lazy εδώ
         ), 
         name='password_reset'),
    path('accounts/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ), 
         name='password_reset_confirm'),
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    path('accounts/password_change/', 
         auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('password_change_done')
         ), 
         name='password_change'),
    path('accounts/password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
         ), 
         name='password_change_done'),     
    # --- End Password Reset URLs ---
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)