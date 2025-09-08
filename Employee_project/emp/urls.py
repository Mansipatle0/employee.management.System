from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path("add/", views.add_employee,name="add_employee"),
    path("update/<int:id>/",views.update_employee,name="update_employee"),
    path("delete/<int:id>/",views.delete_employee,name="delete_employee"),
    
    path("apply/<int:emp_id>/", views.apply_leave,name="apply_leave"),
    path("leave/list//", views.leave_list,name="leave_list"),
    path("leave/approve/<int:leave_id>/",views.approve_leave,name="approve_leave"),
    path("leave/reject/<int:leave_id>/",views.reject_leave,name="reject_leave"),
    
    #path('dashboard/', views.dashboard, name='dashboard'),
    
    
    path('leave_requests/', views.leave_requests, name='leave_requests'),
    
     path('status/<int:emp_id>/', views.my_leaves, name='my_leaves'), 
     
      
    # path('login/', views.login_view, name='login'),
     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
     path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
     path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
     path('intern-dashboard/', views.intern_dashboard, name='intern_dashboard'),
     path('login/', views.user_login, name='login'),
     path('dashboard/', views.login_redirect, name='login_redirect'),
     path('role/', views.role_required, name='role_required'),
     path('logout/', views.logout_view, name='logout_view'),
     path('leave/update/<int:id>/', views.update_leave, name='update_leave'),
     path('leave/delete/<int:id>/', views.delete_leave, name='delete_leave'),
     path('heartbeat/', views.heartbeat, name='heartbeat'),
     path('attendance/update/<int:id>/', views.update_attendance, name='update_attendance'),
     path('attendance/delete/<int:id>/', views.delete_attendance, name='delete_attendance'),
     path('check-in/', views.check_in, name='check_in'),
     path('check-out/', views.check_out, name='check_out'),
     path('intern/check_in/', views.intern_check_in, name='intern_check_in'),
     path('intern/check_out/', views.intern_check_out, name='intern_check_out'),
     
     
     
     
     
     
]
