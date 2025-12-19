# Authentication - Agent Notes

## Overview

This document describes the authentication system for the webapp, specifically focusing on organization-scoped permissions and roles.

## Authentication

The application uses Django's built-in authentication system with django-allauth for social authentication support.

- **User Model**: Django's default `User` model
- **Authentication Backends**:
  - `django.contrib.auth.backends.ModelBackend`
  - `allauth.account.auth_backends.AuthenticationBackend`
- **Session-based authentication**: Users are authenticated via sessions
- **API Authentication**: Token-based authentication via `rest_framework.authtoken`
- **Permissions**: are describe in `./permissions.AGENTS.md`
