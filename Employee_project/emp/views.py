from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Attendance, LeaveRequest
from datetime import date, time, timedelta
from django.db.models import Count
from .forms import LeaveRequestForm, AttendanceForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime


# Show all employees
def index(request):
    employees = Employee.objects.all()
    return render(request, "emp/index.html", {"employees": employees})


# Add new employee
def add_employee(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        department = request.POST["department"]
        salary = request.POST["salary"]
        try:
            Employee.objects.create(name=name, email=email, department=department, salary=salary)
            messages.success(request,"Employee added successfully!")
        except IntegrityError:
            messages.error(request,"Email already exists, please use another email.")
        return redirect("admin_dashboard")
    return render(request, "emp/add_employee.html")


# Update employee
def update_employee(request, id):
    empl = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        empl.name = request.POST["name"]
        empl.email = request.POST["email"]
        empl.department = request.POST["department"]
        empl.salary = request.POST["salary"]
        empl.save()
        return redirect("admin_dashboard")
    return render(request, "emp/update_employee.html", {"empl": empl})


# Delete employee
def delete_employee(request, id):
    empl = get_object_or_404(Employee, id=id)
    empl.delete()
    return redirect("admin_dashboard")


# Employee applies for leave
def apply_leave(request, emp_id=None):
    employee = get_object_or_404(Employee, id=emp_id)
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = "Pending"
            leave.save()
            return redirect("dashboard")  # after applying, go to dashboard
    else:
        form = LeaveRequestForm()
    return render(request, "emp/apply_leave.html", {"form": form, "employee": employee})


# Employee can check his own leave status
def my_leaves(request, emp_id=None):
    employee = get_object_or_404(Employee, id=emp_id)
    leaves = LeaveRequest.objects.filter(employee=employee)
    return render(request, "emp/my_leaves.html", {"employee": employee, "leaves": leaves})


# List of all leaves (HR view)
def leave_list(request):
    leaves = LeaveRequest.objects.all()
    return render(request, "emp/leave_list.html", {"leaves": leaves})


# Approve leave
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = "Approved"
    leave.save()
    return redirect("hr_dashboard")


# Reject leave
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = "Rejected"
    leave.save()
    return redirect("hr_dashboard")

# Pending Leave Requests (HR ke liye)
def leave_requests(request):
    leaves = LeaveRequest.objects.filter(status="Pending")
    return render(request, "emp/leave_requests.html", {"leaves": leaves})


# Dashboard
def dashboard(request):
    today = date.today()

    total_employees = Employee.objects.count()
    present_today = Attendance.objects.filter(date=today).count()
    absent_today = total_employees - present_today
    approved_leaves = LeaveRequest.objects.filter(
        status='Approved', start_date__lte=today, end_date__gte=today
    ).count()
    attendance_percentage = (present_today / total_employees * 100) if total_employees > 0 else 0

    # Late employees
    late_employees = Attendance.objects.filter(date=today, check_in__gt=time(9, 30))
    late_employees_count = late_employees.count()
    pending_leaves = LeaveRequest.objects.filter(status='Pending').count()

    # Department-wise employee count
    dept_count = Employee.objects.values('department').annotate(total=Count('id'))
    dept_names = [d['department'] for d in dept_count]
    dept_totals = [d['total'] for d in dept_count]

    context = {
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'leaves': approved_leaves,
        'dept_names': dept_names,
        'dept_totals': dept_totals,
        'late_employees_count': late_employees_count,
        'attendance_percentage': attendance_percentage,
        'pending_leaves': pending_leaves,
        # employee ka reference agar dashboard se apply/status jaayega
        'employee': Employee.objects.first()  
    }
    return render(request, "emp/dashboard.html", context)


#def login_view(request):
 #   if request.method == "POST":
  #      username = request.POST['username']
   #     password = request.POST['password']
    #    role = request.POST['role']
     #   user = authenticate(request, username=username, password=password)
      #  if user is not None and user.role == role:
       #     login(request, user)
        #    if role == "Admin":
         #       return redirect('admin_dashboard')
          #  elif role == "HR":
           #     return redirect('hr_dashboard')
          #  elif role == "Employee":
           #     return redirect('employee_dashboard')
          #  elif role == "Intern":
           #     return redirect('intern_dashboard')
      #  else:
       #     return render(request, 'emp/login.html', {'error': 'Invalid credentials or role'})
   # return render(request, 'emp/login.html')


def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role.lower() != role.lower():
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# -----------------------------
# Dashboards
# -----------------------------

@role_required('Admin')
def admin_dashboard(request):
    # Admin ko sab employees aur leaves dekhne hai
    employees_list = Employee.objects.all()
    leaves_list = LeaveRequest.objects.all()
    total_employees = employees_list.count()
    attendance_list = Attendance.objects.select_related('employee').all()
    #total_employees = employees_list.count()
    total_attendance = attendance_list.count()
    pending_leaves = leaves_list.filter(status='Pending').count()
    return render(request, 'emp/admin_dashboard.html', {'employees_list': employees_list, 'leaves_list': leaves_list, 'attendance_list': attendance_list, 'total_employees': total_employees, 'total_attendance':total_attendance, 'pending_leaves': pending_leaves})

@role_required('HR')
def hr_dashboard(request):
    # HR ko pending leaves aur employees ki attendance chahiye
    pending_leaves = LeaveRequest.objects.filter(status='Pending')
    employees = Attendance.objects.all()
    approved_leaves = LeaveRequest.objects.filter(status='Approved')
    rejected_leaves = LeaveRequest.objects.filter(status='Rejected')
    
    # Top stats
    total_employees = employees.count()
    pending_leaves_count = pending_leaves.count()
    approved_leaves_count = approved_leaves.count()
    rejected_leaves_count = rejected_leaves.count()
    
    context = {
        'employees': employees,
        'pending_leaves': pending_leaves,
        'total_employees': total_employees,
        'pending_leaves_count': pending_leaves_count,
        'approved_leaves_count': approved_leaves_count,
        'rejected_leaves_count': rejected_leaves_count,
    }
    return render(request, 'emp/hr_dashboard.html', context)

@role_required('Employee')
def employee_dashboard(request):
    try:
        emp = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('login')

    # Attendance (last 10 records)
    attendance_qs = Attendance.objects.filter(employee=emp).order_by('-date')
    attendance = attendance_qs[:10]

    # Leaves
    leaves = LeaveRequest.objects.filter(employee=emp).order_by('-applied_on')

    # Leave Apply Form
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = emp
            leave.save()
            return redirect("employee_dashboard")
    else:
        form = LeaveRequestForm()

    # Extra stats
    total_hours = sum([att.working_hours() for att in attendance_qs])
    total_leaves = leaves.count()
    pending_leaves = leaves.filter(status="Pending").count()
    total_employees = Employee.objects.count()

    return render(request, 'emp/employee_dashboard.html', {
        'attendance': attendance,
        'leaves': leaves,
        'employee': emp,
        'form': form,
        'total_hours': total_hours,
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'total_employees': total_employees,
    })


@role_required('Intern')
def intern_dashboard(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        # Agar Employee record missing hai
        return render(request, 'emp/error.html', {'message': 'Employee record not found. Contact Admin.'})

    attendance = employee.attendance_set.all().order_by('-date')
    leaves = employee.leaverequest_set.all().order_by('-applied_on')

    total_employees = Employee.objects.count()
    total_hours = sum([att.working_hours() or 0 for att in attendance])
    total_leaves = leaves.count()
    pending_leaves = leaves.filter(status='Pending').count()

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = 'Pending'
            leave.save()
            return redirect('intern_dashboard')
    else:
        form = LeaveRequestForm()

    context = {
        'employee': employee,
        'attendance': attendance,
        'leaves': leaves,
        'total_employees': total_employees,
        'total_hours': total_hours,
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'form': form
    }
    return render(request, 'emp/intern_dashboard.html', context)
# -----------------------------
# Tamper-Proof Attendance (Heartbeat)
# -----------------------------
@login_required
def heartbeat(request):
    if request.user.is_authenticated:
        try:
            emp = Employee.objects.get(user=request.user)
            emp.is_online = True
            emp.last_heartbeat = timezone.now()
            emp.save()
            return JsonResponse({'status':'alive'})
        except Employee.DoesNotExist:
            return JsonResponse({'status':'no employee found'})
    return JsonResponse({'status':'not logged in'})

# -----------------------------
# Logout / Auto Check-Out
# -----------------------------
from django.contrib.auth import logout as auth_logout

@login_required
def logout_view(request):
    attendance_id = request.session.get('attendance_id')
    if attendance_id:
        attendance = Attendance.objects.get(id=attendance_id)
        attendance.update_active()  # final working hours
        del request.session['attendance_id']
    auth_logout(request)
    return redirect('login')


          

def user_login(request):
     if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == role:
            login(request, user)
            if role == "Admin":
                return redirect('admin_dashboard')
            elif role == "HR":
                return redirect('hr_dashboard')
            elif role == "Employee":
                return redirect('employee_dashboard')
            elif role == "Intern":
                return redirect('intern_dashboard')
        else:
            return render(request, 'emp/login.html', {'error': 'Invalid credentials or role'})
     return render(request, 'emp/login.html')


           

@login_required
def login_redirect(request):
    # Auto check-in
    emp = Employee.objects.get(user=request.user)
    attendance = Attendance.objects.create(employee=emp)
    request.session['attendance_id'] = attendance.id

    # Role-based dashboard redirect
    if request.user.role == 'Admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'HR':
        return redirect('hr_dashboard')
    elif request.user.role == 'Employee':
        return redirect('employee_dashboard')
    elif request.user.role == 'Intern':
        return redirect('intern_dashboard')

# Update Leave (Admin ke liye)
def update_leave(request, id):
    leave = get_object_or_404(LeaveRequest, id=id)
    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard")
    else:
        form = LeaveRequestForm(instance=leave)
    return render(request, "emp/update_leave.html", {"form": form})

# Delete Leave (Admin ke liye)
def delete_leave(request, id):
    leave = get_object_or_404(LeaveRequest, id=id)
    leave.delete()
    return redirect("admin_dashboard")


def employee_login(request):
    if request.user.is_authenticated:
        today = timezone.now().date()
        # Aaj ki entry already hai ya nahi check karo
        attendance = Attendance.objects.filter(employee=request.user, check_in__date=today).last()
        
        if not attendance:  # agar nahi hai to nayi entry banao
            Attendance.objects.create(employee=request.user, check_in=timezone.now())
        
        return redirect("employee_dashboard")


def employee_logout(request):
    if request.user.is_authenticated:
        # Latest record uthao jiska checkout abhi null hai
        attendance = Attendance.objects.filter(employee=request.user, check_out__isnull=True).last()
        
        if attendance:
            attendance.check_out = timezone.now()

            # Working hours calculate karo
            if attendance.check_in:
                diff = attendance.check_out - attendance.check_in
                attendance.working_hours = round(diff.total_seconds() / 3600, 2)  # in hours (2 decimal)
            
            attendance.save()
        
        return redirect("login")
    
    # Attendance update
def update_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard")
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, "emp/update_attendance.html", {"form": form})

# Attendance delete
def delete_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    attendance.delete()
    return redirect("admin_dashboard")

def add_attendance(request):
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            # Agar check-in aur check-out dono fill kiye hain to hours calculate karo
            if attendance.check_in and attendance.acheck_out:
                fmt = "%H:%M:%S"
                t1 = datetime.strptime(str(attendance.check_in), fmt)
                t2 = datetime.strptime(str(attendance.check_out), fmt)
                total_seconds = (t2 - t1).seconds
                attendance.working_hours = round(total_seconds / 3600, 2)  # 2 decimal hours me

            attendance.save()
            return redirect("admin_dashboard")  # redirect to your dashboard
        else:
                form = AttendanceForm()

    return render(request, "emp/add_attendance.html", {"form": form})

#role_required('Employee')
def check_in(request):
    emp = Employee.objects.get(user=request.user)
    
   # print("DEBUG:User role =",emp.role)
    #role = str(emp.role).strip().lower()
   # if emp.role not in['Employee','Intern']:
        #messages.error(request,"you do not have permission to access this page.")
       # return redirect('login')
    # Agar already check-in hai aur check-out nahi kiya
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(employee=emp, date=today)

    if attendance.check_in:
        messages.warning(request, "You already checked in today!")
    else:
        attendance.check_in = timezone.now()
        attendance.save()
        emp.is_online = True
        emp.last_heartbeat = timezone.now()
        emp.save()
        messages.success(request, f"Checked in at {attendance.check_in.strftime('%H:%M')}")

    return redirect('employee_dashboard')


@role_required('Employee')
def check_out(request):
    emp = Employee.objects.get(user=request.user)

    today = timezone.now().date()
    try:
        attendance = Attendance.objects.get(employee=emp, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, "You have not checked in today!")
        return redirect('employee_dashboard')

    if attendance.check_out:
        messages.warning(request, "You already checked out today!")
    else:
        attendance.check_out = timezone.now()
        #diff = attendance.check_out - attendance.check_in
        attendance.total_hours = attendance.working_hours()
        attendance.save()
        emp.is_online = False
        emp.save()
        messages.success(request, f"Checked out at {attendance.check_out.strftime('%H:%M')}")

    return redirect('employee_dashboard')

# Intern Check-in
def intern_check_in(request):
    emp = Employee.objects.filter(user=request.user).first()
    if not emp:
        messages.error(request, "Employee record not found!")
        return redirect('login')

    if str(emp.role).strip().lower() != 'intern':
        messages.error(request, "You do not have access to this page.")
        return redirect('login')

    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(employee=emp, date=today)

    if attendance.check_in:
        messages.warning(request, "You already checked in today!")
    else:
        attendance.check_in = timezone.now()
        attendance.save()
        messages.success(request, f"Checked in at {attendance.check_in.strftime('%H:%M')}")

    return redirect('intern_dashboard')


# Intern Check-out
def intern_check_out(request):
    emp = Employee.objects.get(user=request.user)

    today = timezone.now().date()
    try:
        attendance = Attendance.objects.get(employee=emp, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, "You have not checked in today!")
        return redirect('employee_dashboard')

    if attendance.check_out:
        messages.warning(request, "You already checked out today!")
    else:
        attendance.check_out = timezone.now()
        #diff = attendance.check_out - attendance.check_in
        attendance.total_hours = attendance.working_hours()
        attendance.save()
        emp.is_online = False
        emp.save()
        messages.success(request, f"Checked out at {attendance.check_out.strftime('%H:%M')}")

    return redirect('employee_dashboard')

    
    
    
    
    
    
    
    
    
    
    
    #emp = Employee.objects.get(user=request.user)

    #today = timezone.now().date()
   # try:
       # attendance = Attendance.objects.get(employee=emp, date=today)
   # except Attendance.DoesNotExist:
      #  messages.error(request, "You have not checked in today!")
       # return redirect('employee_dashboard')

    #if attendance.check_out:
       # messages.warning(request, "You already checked out today!")
   # else:
       # attendance.check_out = timezone.now()
        #diff = attendance.check_out - attendance.check_in
       # attendance.total_hours = attendance.working_hours()
       # attendance.save()
       # emp.is_online = False
        #emp.save()
        #messages.success(request, f"Checked out at {attendance.check_out.strftime('%H:%M')}")

    #return redirect('employee_dashboard')


    
    
    
   # emp = Employee.objects.filter(user=request.user).first()
   # if not emp:
    #    messages.error(request, "Employee record not found!")
     #   return redirect('login')

    #if str(emp.role).strip().lower() != 'intern':
     #  messages.error(request, "You do not have access to this page.")
      #  return redirect('login')

   # today = timezone.now.date()
    #try:
     #   attendance = Attendance.objects.get(employee=emp, date=today)
    #except Attendance.DoesNotExist:
     #   messages.error(request, "You have not checked in today!")
      #  return redirect('intern_dashboard')

   # if attendance.check_out:
    #    messages.warning(request, "You already checked out today!")
    #else:
    #    attendance.check_out = timezone.now()
     #   attendance.total_hours = attendance.working_hours()
      #  attendance.save()
       # messages.success(request, f"Checked out at {attendance.check_out.strftime('%H:%M')} | Total Hours: {attendance.total_hours}")

    #turn redirect('intern_dashboard')
    