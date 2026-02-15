from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard (landing page)
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Posts (status updates)
    path('posts/', views.posts_view, name='posts'),
    
    # Profile
    path('profile/edit/', login_required(views.ProfileEditView.as_view()), name='profile_edit'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]
