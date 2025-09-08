from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
   #from django.conf import settings
from datetime import datetime,timedelta

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True , blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10,decimal_places=2)
    ROLE_CHOICES = (
        ('Employee','Employee'),
        ('Intern','Intern'),
        ('HR','HR'),
        ('Admin','Admin'),
    )
    role = models.CharField(max_length=20,choices=ROLE_CHOICES)
    
    #heartbeat status
    is_online = models.BooleanField(default=False)
    last_heartbeat = models.DateTimeField(null=True,blank=True)
    
    
    
    def __str__(self):
        return f"{self.name} | {self.email} | {self.department}" 
    
#new model:Leave
class Leave(models.Model):
   employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    # kis employee ka leave hai
   leave_type=models.CharField(max_length=50,choices=[
       ("Sick", "Sick"),("Casual", "Casual"),("Paid", "Paid")])
   start_date = models.DateField() # leave kab start ho rahi hai
   end_date = models.DateField() # leave kab end hogi
   reason = models.TextField()
   status = models.CharField(max_length=20,choices=[
        ("Pending", "Pending"),("Approved", "Approved"),("Rejected", "Rejected")], default="Pending")
   #class Meta:
    #   db_table ="emp_leave"
   def __str__(self):
       return f"{self.employee.name} | {self.leave_type} | {self.status}" 
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
        # kis employee ka attendance hai
    date = models.DateField(auto_now_add=True)#Attendance ki date
    check_in = models.DateTimeField(null=True,blank=True) #check_in time
    check_out = models.DateTimeField(null=True,blank=True) #check_out time
    #working_hours = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    total_hours = models.FloatField(default=0)
    
    def working_hours(self):
        if self.check_in and self.check_out:
           # check_in_dt = datetime.combine(self.date, self.check_in)
           # check_out_dt = datetime.combine(self.date, self.check_out)
            diff = self.check_out -self.check_in
            hours = diff.total_seconds() / 3600
            return round(hours, 2)  # 2 decimal places
        return 0
    @property
    def is_online(self):
        return self.check_in is not None and self.check_out is None
    
    #def __str__(self):
     #   return f"{self.employee.name} {self.date}"
    

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)   # jisne request dali
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    leave_type = models.CharField(max_length=50)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    
   # class Meta:
      #  db_table = "emp_leave_request"
   # def __str__(self):
   #     return f"{self.employee.name} - {self.status}"
    

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('HR', 'HR'),
        ('Employee', 'Employee'),
        ('Intern', 'Intern'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    
    class Meta:
        db_table = 'emp_customuser'

    # Groups & permissions ke liye unique related_name
    groups = models.ManyToManyField(
        Group,
        related_name="custom_users",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"