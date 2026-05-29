"""
SafeHer API Views — Django REST Framework
All persistence is handled through Supabase.
"""

import hashlib
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .supabase_client import get_supabase, get_supabase_service
from .auth import generate_token, require_auth, require_admin


# =========================
# Helpers
# =========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# Register
# =========================

@api_view(['POST'])
def register(request):
    data = request.data

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not all([name, email, phone, password]):
        return Response({'error': 'All fields are required'}, status=400)

    sb = get_supabase()

    existing = sb.table('users').select('*').eq('email', email).execute()

    if existing.data:
        return Response({'error': 'Email already exists'}, status=400)

    result = sb.table('users').insert({
        'name': name,
        'email': email,
        'phone': phone,
        'password_hash': hash_password(password)
    }).execute()

    return Response({
        'message': 'User registered successfully',
        'user': result.data[0]
    })


# =========================
# Login
# =========================

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    sb = get_supabase()

    result = sb.table('users').select('*').eq(
        'email', email
    ).eq(
        'password_hash', hash_password(password)
    ).execute()

    if not result.data:
        return Response({'error': 'Invalid credentials'}, status=401)

    user = result.data[0]

    token = generate_token({
        'user_id': user['id'],
        'email': user['email'],
        'role': 'user'
    })

    return Response({
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
    })


# =========================
# Admin Login
# =========================

@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username != settings.ADMIN_USERNAME or password != settings.ADMIN_PASSWORD:
        return Response({'error': 'Invalid admin credentials'}, status=401)

    token = generate_token({
        'username': username,
        'role': 'admin'
    })

    return Response({
        'token': token,
        'admin': {
            'username': username
        }
    })


# =========================
# Incidents
# =========================

@api_view(['GET', 'POST'])
@require_auth
def incidents(request):

    sb = get_supabase()

    user_id = request.user_payload['user_id']

    if request.method == 'POST':

        incident_type = request.data.get('incident_type')
        description = request.data.get('description')
        location = request.data.get('location')

        result = sb.table('incidents').insert({
            'user_id': user_id,
            'incident_type': incident_type,
            'description': description,
            'location': location,
            'status': 'pending'
        }).execute()

        return Response({
            'message': 'Incident reported',
            'data': result.data[0]
        })

    result = sb.table('incidents').select('*').eq(
        'user_id', user_id
    ).execute()

    return Response(result.data)


# =========================
# Contacts
# =========================

@api_view(['GET', 'POST'])
@require_auth
def contacts(request):

    sb = get_supabase()

    user_id = request.user_payload['user_id']

    if request.method == 'POST':

        name = request.data.get('name')
        phone = request.data.get('phone')
        relationship = request.data.get('relationship')

        result = sb.table('emergency_contacts').insert({
            'user_id': user_id,
            'name': name,
            'phone': phone,
            'relationship': relationship
        }).execute()

        return Response(result.data[0])

    result = sb.table('emergency_contacts').select('*').eq(
        'user_id', user_id
    ).execute()

    return Response(result.data)


# =========================
# Delete Contact
# =========================

@api_view(['DELETE'])
@require_auth
def contact_detail(request, contact_id):

    sb = get_supabase()

    user_id = request.user_payload['user_id']

    sb.table('emergency_contacts').delete().eq(
        'id', contact_id
    ).eq(
        'user_id', user_id
    ).execute()

    return Response({'message': 'Contact deleted'})


# =========================
# SOS
# =========================

@api_view(['POST'])
def sos_alert(request):

    sb = get_supabase()

    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    result = sb.table('sos_alerts').insert({
        'latitude': latitude,
        'longitude': longitude,
        'status': 'active'
    }).execute()

    return Response({
        'message': 'SOS alert sent',
        'data': result.data[0]
    })


# =========================
# Admin Stats
# =========================

@api_view(['GET'])
@require_admin
def admin_stats(request):

    sb = get_supabase_service()

    users = sb.table('users').select('*').execute()
    incidents = sb.table('incidents').select('*').execute()
    sos = sb.table('sos_alerts').select('*').execute()

    return Response({
        'total_users': len(users.data),
        'total_incidents': len(incidents.data),
        'total_sos': len(sos.data),
        'resolved': 0
    })


# =========================
# Admin Incidents
# =========================

@api_view(['GET'])
@require_admin
def admin_incidents(request):

    sb = get_supabase_service()

    result = sb.table('incidents').select('*').execute()

    return Response(result.data)


# =========================
# Admin SOS
# =========================

@api_view(['GET'])
@require_admin
def admin_sos(request):

    sb = get_supabase_service()

    result = sb.table('sos_alerts').select('*').execute()

    return Response(result.data)


# =========================
# Admin Users
# =========================

@api_view(['GET'])
@require_admin
def admin_users(request):

    sb = get_supabase_service()

    result = sb.table('users').select('*').execute()

    return Response(result.data)

from django.http import HttpResponse

def home(request):
    return HttpResponse("✅ SafeHer Backend is Running Successfully")