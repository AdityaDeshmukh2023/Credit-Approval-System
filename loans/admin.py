from django.contrib import admin
from .models import Customer, Loan


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']
    list_filter = ['age']
    search_fields = ['first_name', 'last_name', 'phone_number']
    readonly_fields = ['customer_id', 'approved_limit']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer_id', 'first_name', 'last_name', 'age', 'phone_number')
        }),
        ('Financial Information', {
            'fields': ('monthly_salary', 'approved_limit', 'current_debt')
        }),
    )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'emis_paid_on_time', 'start_date', 'end_date', 'is_active']
    list_filter = ['start_date', 'end_date', 'interest_rate', 'tenure']
    search_fields = ['loan_id', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['loan_id', 'monthly_repayment', 'repayments_left', 'is_active']
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate')
        }),
        ('Payment Information', {
            'fields': ('monthly_repayment', 'emis_paid_on_time', 'repayments_left')
        }),
        ('Date Information', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    ) 