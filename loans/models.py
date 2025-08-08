from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import math


class Customer(models.Model):
    """Customer model for storing customer information"""
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone_number = models.BigIntegerField(unique=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_approved_limit(self):
        """Calculate approved limit based on monthly salary"""
        # 36 * monthly_salary rounded to nearest lakh
        limit = float(self.monthly_salary) * 36
        # Round to nearest lakh (100000)
        return round(limit / 100000) * 100000

    def save(self, *args, **kwargs):
        if not self.approved_limit:
            self.approved_limit = self.calculate_approved_limit()
        super().save(*args, **kwargs)


class Loan(models.Model):
    """Loan model for storing loan information"""
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(60)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.full_name}"

    def calculate_monthly_repayment(self):
        """Calculate monthly repayment using compound interest formula"""
        if self.interest_rate <= 0 or self.tenure <= 0:
            return 0
        
        # Convert annual interest rate to monthly
        monthly_rate = float(self.interest_rate) / 100 / 12
        
        # Calculate EMI using compound interest formula
        principal = float(self.loan_amount)
        if monthly_rate == 0:
            return principal / self.tenure
        
        emi = principal * (monthly_rate * (1 + monthly_rate) ** self.tenure) / ((1 + monthly_rate) ** self.tenure - 1)
        return round(emi, 2)

    def save(self, *args, **kwargs):
        if not self.monthly_repayment:
            self.monthly_repayment = self.calculate_monthly_repayment()
        super().save(*args, **kwargs)

    @property
    def repayments_left(self):
        """Calculate remaining EMIs"""
        return self.tenure - self.emis_paid_on_time

    @property
    def is_active(self):
        """Check if loan is still active"""
        from django.utils import timezone
        return timezone.now().date() <= self.end_date 