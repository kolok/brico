# Authentication - Agent Notes

This document describes the authentication system for the webapp, covering user authentication, session management, API token authentication, and integration with django-allauth.

## Overview

The application uses **Django's built-in authentication system** with **django-allauth** for enhanced capabilities including social authentication, email verification, and password management.

- **User Model**: Django's default `User` model
- **Session-based auth**: Traditional session cookies for web browsers
- **Token-based auth**: REST API token authentication for mobile/external clients
- **Social auth**: Optional social login via django-allauth
- **Email verification**: Optional email confirmation on signup
- **Multi-factor auth**: Supported via django-allauth plugins

## Authentication System

### User Model

Uses Django's default `User` model with standard fields:

- `username`: Unique username
- `email`: Email address
- `password`: Hashed password
- `first_name`, `last_name`: Optional
- `is_active`: Controls account access
- `is_staff`, `is_superuser`: Permission levels

Extend with custom fields in a user profile model if needed (e.g., preferences, metadata).

### Authentication Backends

The system is configured with multiple backends:

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Standard auth
    'allauth.account.auth_backends.AuthenticationBackend',  # django-allauth
]
```

Users can authenticate via:

- **Username + password**
- **Email + password** (allauth)
- **Social accounts** (GitHub, Google, etc. via allauth)

### Session-Based Authentication

Used for web browser access. Django creates a session cookie on login.

**How it works**:

1. User submits login form (username/email + password)
2. Django authenticates credentials
3. Session is created, session ID stored in cookie
4. Subsequent requests include session cookie
5. User is authenticated via session on each request

**Configuration**:

```python
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # JavaScript cannot access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

### Token-Based API Authentication

Used for REST API access from mobile apps or external clients.

**How it works**:

1. User authenticates (login)
2. Token is generated/retrieved (unique per user)
3. Client includes token in `Authorization: Token <token>` header
4. API authenticates request via token
5. No session cookie needed

**Configuration**:

```python
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

**Getting a token**:

```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=john&password=secret"
```

Returns:

```json
{ "token": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" } // pragma: allowlist secret
```

**Using token in API requests**:

```bash
# pragma: allowlist secret
curl -H "Authorization: Token aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
  http://localhost:8000/api/audits/
```

## Login & Logout

### Login View

For web browsers, use django-allauth login:

```python
# urls.py
urlpatterns = [
    path('accounts/', include('allauth.urls')),
]

# Template: signup/login.html
<form method="post" action="{% url 'account_login' %}">
    {% csrf_token %}
    {{ form }}
    <button type="submit">Sign In</button>
</form>
```

Or implement custom login:

```python
# views.py
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Invalid credentials
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')
```

### Logout View

```python
# views.py
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')

# urls.py
path('logout/', logout_view, name='logout'),

# Template
<a href="{% url 'logout' %}">Sign Out</a>
```

Or use django-allauth:

```html
<a href="{% url 'account_logout' %}">Sign Out</a>
```

## Sign Up

### Using django-allauth

Enable in `settings.py`:

```python
INSTALLED_APPS = [
    'allauth',
    'allauth.account',
]

ACCOUNT_EMAIL_REQUIRED = True  # Require email
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # 'mandatory', 'optional', 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Allow both
ACCOUNT_USERNAME_REQUIRED = True
```

Template:

```html
<form method="post" action="{% url 'account_signup' %}">
  {% csrf_token %} {{ form }}
  <button type="submit">Sign Up</button>
</form>
```

### Custom Sign Up

```python
# views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')
```

## API Token Management

### Getting User's Token

```python
# views.py
from rest_framework.authtoken.models import Token

def get_token(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'token': str(token)})
```

### Regenerating Token

```python
def regenerate_token(request):
    request.user.auth_token.delete()
    new_token = Token.objects.create(user=request.user)
    return JsonResponse({'token': str(new_token)})
```

### Token Authentication in Views

```python
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    return JsonResponse({'message': f'Hello, {request.user.username}!'})
```

## Common Patterns

### Protecting Views

**Web views** (session-based):

```python
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
```

**API views** (token-based):

```python
from rest_framework.permissions import IsAuthenticated

class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    permission_classes = [IsAuthenticated]
```

### Accessing Authenticated User

In views:

```python
def my_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
    else:
        # Handle unauthenticated
        pass
```

In templates:

```html
{% if user.is_authenticated %}
<p>Welcome, {{ user.first_name }}!</p>
<a href="{% url 'logout' %}">Logout</a>
{% else %}
<a href="{% url 'login' %}">Login</a>
<a href="{% url 'signup' %}">Sign Up</a>
{% endif %}
```

### User Registration & Profile

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Create profile on user creation
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
```

## Password Management

### Password Reset

Using django-allauth (recommended):

```html
<!-- In template -->
<a href="{% url 'account_reset_password' %}">Forgot password?</a>
```

Or custom implementation:

```python
# views.py
from django.contrib.auth.views import PasswordResetView

class CustomPasswordReset(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.html'
```

### Password Change

```python
# views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
```

## Testing Authentication

### Test Login

```python
# tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='john', password='secret')

    def test_login(self):
        response = self.client.post('/login/', {
            'username': 'john',
            'password': 'secret' # pragma: allowlist secret
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_protected_view(self):
        self.client.login(username='john', password='secret') # pragma: allowlist secret
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_protected_view_unauthenticated(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
```

### Test Token Authentication

```python
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

class APIAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='john', password='secret')
        self.token = Token.objects.create(user=self.user)

    def test_api_with_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/audits/')
        self.assertEqual(response.status_code, 200)

    def test_api_without_token(self):
        response = self.client.get('/api/audits/')
        self.assertEqual(response.status_code, 401)  # Unauthorized
```

## Security Best Practices

### Password Storage

- Passwords are **always hashed** (never stored in plain text)
- Django uses PBKDF2 by default, configurable in settings
- Use `User.objects.create_user()` to hash passwords automatically

### Session Security

- **HTTPS only**: Set `SESSION_COOKIE_SECURE = True` in production
- **HttpOnly flag**: Set `SESSION_COOKIE_HTTPONLY = True` to prevent JavaScript access
- **SameSite**: Set `SESSION_COOKIE_SAMESITE = 'Lax'` for CSRF protection
- **Expiration**: Set appropriate `SESSION_COOKIE_AGE`

### API Token Security

- Tokens should be **stored securely** on client (encrypted if possible)
- **Never log or expose tokens** in error messages
- Implement **token expiration** if needed
- Allow users to **regenerate/revoke tokens**

### CSRF Protection

- All POST/PUT/DELETE forms must include `{% csrf_token %}`
- Django verifies CSRF tokens on state-changing requests
- API endpoints should use token authentication (tokens are exempt from CSRF)

### Common Vulnerabilities to Avoid

- ❌ Don't store passwords in plain text
- ❌ Don't expose tokens in URLs or logs
- ❌ Don't skip CSRF protection on forms
- ❌ Don't use weak password requirements
- ❌ Don't log sensitive information

## Configuration

### Essential Settings

```python
# settings.py

# Session
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# django-allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_USERNAME_REQUIRED = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Related Documentation

- **Permissions & Authorization**: See `./permissions.AGENTS.md` for role-based access control and object-level permissions
- **Environment setup**: See `./env.AGENTS.md` for email configuration and other auth-related env variables
