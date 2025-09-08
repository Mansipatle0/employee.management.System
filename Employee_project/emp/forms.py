from django import forms
from .models import LeaveRequest, Attendance

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        exclude = ['employee','status']
        fields = ['leave_type','start_date','end_date','reason', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date'}),
            'end_date': forms.DateInput(attrs={'type':'date'}),
            'reason': forms.Textarea(attrs={'rows':3}),
            'status': forms.Select(attrs={'class':'form-input'}),
        }
            
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude =["date"]
        fields = ["employee","date","check_in","check_out"]
        