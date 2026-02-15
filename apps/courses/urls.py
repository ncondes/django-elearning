from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course list and search
    path('', views.CourseListView.as_view(), name='course_list'),
    
    # Course CRUD
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    
    # Enrollment
    path('<int:pk>/enroll/', views.enroll_course, name='enroll'),
    path('<int:pk>/unenroll/', views.unenroll_course, name='unenroll'),
    
    # Feedback
    path('<int:pk>/feedback/', views.leave_feedback, name='leave_feedback'),
    
    # Materials
    path('<int:pk>/materials/upload/', views.upload_material, name='upload_material'),
    path('<int:pk>/materials/<int:material_pk>/delete/', views.delete_material, name='delete_material'),
    
    # Student management
    path('<int:pk>/students/<int:student_pk>/block/', views.block_student, name='block_student'),
    path('<int:pk>/students/<int:student_pk>/unblock/', views.unblock_student, name='unblock_student'),
    
    # User search (teachers only)
    path('search/users/', views.UserSearchView.as_view(), name='user_search'),
]
