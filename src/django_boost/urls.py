"""
URL configuration for Django Boost.

Provides the browser-logs endpoint and any future Boost routes.
"""

from django.urls import path

from . import views

app_name = "django_boost"

urlpatterns = [
    path("_boost/browser-logs", views.browser_logs, name="browser-logs"),
]
