from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import User, StatusUpdate
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, StatusUpdateForm


class RegisterView(CreateView):
    """User registration view."""
    
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome, {self.object.username}! Your account has been created.')
        return response


class CustomLoginView(LoginView):
    """Custom login view."""
    
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    
    next_page = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out.')
        return super().dispatch(request, *args, **kwargs)


@login_required
@never_cache
def dashboard_view(request):
    """User dashboard - redirects to courses page (sidebar layout makes home redundant)."""
    return redirect('courses:course_list')


@login_required
@never_cache
def posts_view(request):
    """User posts / status updates page."""
    user = request.user
    all_posts = user.status_updates.all()
    
    # Recent posts (5 latest)
    recent_posts = all_posts[:5]
    
    # All posts paginated (excluding the 5 recent ones shown above)
    all_posts_list = list(all_posts[5:])
    paginator = Paginator(all_posts_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = user
            status.save()
            messages.success(request, 'Status update posted!')
            return redirect('accounts:posts')
    else:
        form = StatusUpdateForm()
    
    context = {
        'recent_posts': recent_posts,
        'page_obj': page_obj,
        'total_posts': all_posts.count(),
        'form': form,
    }
    return render(request, 'accounts/posts.html', context)


class ProfileView(DetailView):
    """View user profile."""
    
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_updates'] = self.object.status_updates.all()[:10]
        return context


class ProfileEditView(UpdateView):
    """Edit user profile."""
    
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:dashboard')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
