from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Home / Dashboard
    path('', views.home_view, name='home'),
    
    # Profile
    path('profile/edit/', login_required(views.ProfileEditView.as_view()), name='profile_edit'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]
