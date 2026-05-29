from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path('register/', views.register),
    path('login/', views.login),
    path('admin/login/', views.admin_login),

    # Incidents
    path('incidents/', views.incidents),

    # Emergency Contacts
    path('contacts/', views.contacts),
    path('contacts/<int:contact_id>/', views.contact_detail),

    # SOS
    path('sos/', views.sos_alert),

    # Admin Dashboard
    path('admin/stats/', views.admin_stats),
    path('admin/incidents/', views.admin_incidents),
    path('admin/sos/', views.admin_sos),
    path('admin/users/', views.admin_users),

]