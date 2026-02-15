from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import Course, CourseMaterial, Enrollment, CourseFeedback
from .forms import CourseForm, CourseMaterialForm, CourseFeedbackForm
from apps.accounts.models import User


class TeacherRequiredMixin(UserPassesTestMixin):
    """Mixin that requires the user to be a teacher."""
    
    def test_func(self):
        return self.request.user.is_teacher


class CourseListView(LoginRequiredMixin, ListView):
    """List all active courses."""
    
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        if self.request.user.is_teacher:
            context['my_courses'] = Course.objects.filter(teacher=self.request.user)
        else:
            context['my_enrollments'] = Enrollment.objects.filter(
                student=self.request.user, is_active=True
            ).select_related('course')
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    """View course details."""
    
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object
        
        # Check if user is enrolled
        enrollment = None
        if not user.is_teacher:
            enrollment = Enrollment.objects.filter(
                student=user, course=course
            ).first()
        
        context['enrollment'] = enrollment
        context['is_teacher_owner'] = user == course.teacher
        context['materials'] = course.materials.all()
        context['feedbacks'] = CourseFeedback.objects.filter(
            enrollment__course=course
        ).select_related('enrollment__student')
        
        # Check if student can leave or edit feedback
        if enrollment:
            existing_feedback = getattr(enrollment, 'feedback', None)
            if existing_feedback:
                context['can_edit_feedback'] = True
                context['user_feedback'] = existing_feedback
                context['feedback_form'] = CourseFeedbackForm(instance=existing_feedback)
            else:
                context['can_leave_feedback'] = True
                context['feedback_form'] = CourseFeedbackForm()
        
        return context


class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """Create a new course (teachers only)."""
    
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('courses:course_list')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    """Update a course (owner teacher only)."""
    
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    """Delete a course (owner teacher only)."""
    
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:course_list')
    
    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Course deleted successfully!')
        return super().form_valid(form)


@login_required
def enroll_course(request, pk):
    """Enroll a student in a course."""
    course = get_object_or_404(Course, pk=pk, is_active=True)
    
    if request.user.is_teacher:
        messages.error(request, 'Teachers cannot enroll in courses.')
        return redirect('courses:course_detail', pk=pk)
    
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        messages.success(request, f'You have enrolled in "{course.title}"!')
    elif not enrollment.is_active:
        enrollment.is_active = True
        enrollment.save()
        messages.success(request, f'You have re-enrolled in "{course.title}"!')
    elif enrollment.is_blocked:
        messages.error(request, 'You have been blocked from this course.')
    else:
        messages.info(request, 'You are already enrolled in this course.')
    
    return redirect('courses:course_detail', pk=pk)


@login_required
def unenroll_course(request, pk):
    """Unenroll a student from a course."""
    course = get_object_or_404(Course, pk=pk)
    
    enrollment = get_object_or_404(
        Enrollment, student=request.user, course=course
    )
    
    enrollment.is_active = False
    enrollment.save()
    messages.success(request, f'You have unenrolled from "{course.title}".')
    
    return redirect('courses:course_list')


@login_required
def leave_feedback(request, pk):
    """Leave or update feedback for a course."""
    course = get_object_or_404(Course, pk=pk)
    enrollment = get_object_or_404(
        Enrollment, student=request.user, course=course, is_active=True
    )
    
    # Check if user already has feedback (for editing)
    existing_feedback = getattr(enrollment, 'feedback', None)
    
    if request.method == 'POST':
        form = CourseFeedbackForm(request.POST, instance=existing_feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.enrollment = enrollment
            feedback.save()
            if existing_feedback:
                messages.success(request, 'Your review has been updated!')
            else:
                messages.success(request, 'Thank you for your feedback!')
            return redirect('courses:course_detail', pk=pk)
        else:
            # Form is invalid - show error message
            messages.error(request, 'Please select a rating (1-5 stars) to submit your review.')
    
    return redirect('courses:course_detail', pk=pk)


@login_required
def upload_material(request, pk):
    """Upload course material (teacher only)."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material uploaded successfully!')
            return redirect('courses:course_detail', pk=pk)
    else:
        form = CourseMaterialForm()
    
    return render(request, 'courses/upload_material.html', {
        'form': form,
        'course': course
    })


@login_required
def delete_material(request, pk, material_pk):
    """Delete course material (teacher only)."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    material = get_object_or_404(CourseMaterial, pk=material_pk, course=course)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully!')
    
    return redirect('courses:course_detail', pk=pk)


@login_required
def block_student(request, pk, student_pk):
    """Block a student from a course (teacher only)."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    enrollment = get_object_or_404(
        Enrollment, course=course, student_id=student_pk
    )
    
    if request.method == 'POST':
        enrollment.is_blocked = True
        enrollment.is_active = False
        enrollment.save()
        messages.success(request, f'{enrollment.student.username} has been blocked from this course.')
    
    return redirect('courses:course_detail', pk=pk)


@login_required
def unblock_student(request, pk, student_pk):
    """Unblock a student from a course (teacher only)."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    enrollment = get_object_or_404(
        Enrollment, course=course, student_id=student_pk
    )
    
    if request.method == 'POST':
        enrollment.is_blocked = False
        enrollment.save()
        messages.success(request, f'{enrollment.student.username} has been unblocked.')
    
    return redirect('courses:course_detail', pk=pk)


class UserSearchView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    """Search for users (teachers only)."""
    
    model = User
    template_name = 'courses/user_search.html'
    context_object_name = 'users'
    paginate_by = 15
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        user_type = self.request.GET.get('type', '')
        
        if not query:
            return User.objects.none()
        
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(pk=self.request.user.pk)
        
        if user_type in ['student', 'teacher']:
            queryset = queryset.filter(user_type=user_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['user_type'] = self.request.GET.get('type', '')
        return context
