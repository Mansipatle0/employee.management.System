from django.contrib import admin
from .models import Employee, Attendance, LeaveRequest, CustomUser
from django.contrib.auth.admin import UserAdmin

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department", "salary") #columns


class LeaveAdmin(admin.ModelAdmin):
    list_display = ("leave_type", "start_date", "end_date", "reason", "status")#columns
    
    def employee_name(self, obj):
        return obj.employee.name
    employee_name.admin_order_field = 'employee'
    employee_name.short_description ='Employee'
    
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee','date','check_in','check_out')
    list_filter = ('date','employee')
    
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee','start_date','end_date','reason','status')
    list_filter = ('status','start_date','end_date')
    search_fields = ('employee_username','reason')
    actions = ['approve_leave','reject_leave']
    def approve_leave(self, request, queryset):
        queryset.update(status='Approved')
        self.message_user(request, "Selected leave requests have been approved.")
    approve_leave.short_description = "Approve selected leave requests"

    def reject_leave(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, "Selected leave requests have been rejected.")
    reject_leave.short_description = "Reject selected leave requests"
    

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Employee, EmployeeAdmin)
#admin.site.register(Leave, LeaveAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)


# Register your models here.
