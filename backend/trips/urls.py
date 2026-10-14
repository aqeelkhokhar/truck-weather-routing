from django.urls import path

from trips import views

urlpatterns = [
    path("health/", views.health),
    path("plan/", views.plan),
]
