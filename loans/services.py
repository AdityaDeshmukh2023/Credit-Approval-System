from decimal import Decimal
from django.utils import timezone
from datetime import datetime, date
from .models import Customer, Loan


class CreditScoreService:
    """Service for calculating credit scores and loan eligibility"""
    
    @staticmethod
    def calculate_credit_score(customer):
        """
        Calculate credit score based on historical loan data
        Returns a score out of 100
        """
        try:
            # Get all loans for the customer
            loans = Loan.objects.filter(customer=customer)
            
            if not loans.exists():
                return 50  # Default score for new customers
            
            # Check if current debt exceeds approved limit
            current_debt = sum(loan.loan_amount for loan in loans if loan.is_active)
            if current_debt > float(customer.approved_limit):
                return 0
            
            # Calculate components
            past_loans_paid_on_time = CreditScoreService._calculate_past_loans_score(loans)
            number_of_loans = CreditScoreService._calculate_loan_count_score(loans)
            current_year_activity = CreditScoreService._calculate_current_year_score(loans)
            loan_volume = CreditScoreService._calculate_loan_volume_score(loans, customer)
            
            # Weighted average of components
            credit_score = (
                past_loans_paid_on_time * 0.4 +
                number_of_loans * 0.2 +
                current_year_activity * 0.2 +
                loan_volume * 0.2
            )
            
            return min(100, max(0, round(credit_score)))
            
        except Exception as e:
            print(f"Error calculating credit score: {e}")
            return 0
    
    @staticmethod
    def _calculate_past_loans_score(loans):
        """Calculate score based on past loans paid on time"""
        if not loans.exists():
            return 50
        
        total_emis = sum(loan.tenure for loan in loans)
        emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
        
        if total_emis == 0:
            return 50
        
        on_time_percentage = (emis_paid_on_time / total_emis) * 100
        return min(100, on_time_percentage)
    
    @staticmethod
    def _calculate_loan_count_score(loans):
        """Calculate score based on number of loans taken"""
        loan_count = loans.count()
        
        if loan_count == 0:
            return 50
        elif loan_count == 1:
            return 70
        elif loan_count == 2:
            return 80
        elif loan_count <= 5:
            return 90
        else:
            return 100
    
    @staticmethod
    def _calculate_current_year_score(loans):
        """Calculate score based on loan activity in current year"""
        current_year = timezone.now().year
        current_year_loans = loans.filter(start_date__year=current_year)
        
        if current_year_loans.exists():
            return 100
        else:
            return 50
    
    @staticmethod
    def _calculate_loan_volume_score(loans, customer):
        """Calculate score based on loan approved volume"""
        total_loan_volume = sum(loan.loan_amount for loan in loans)
        approved_limit = float(customer.approved_limit)
        
        if approved_limit == 0:
            return 50
        
        utilization_percentage = (total_loan_volume / approved_limit) * 100
        
        if utilization_percentage <= 30:
            return 100
        elif utilization_percentage <= 50:
            return 80
        elif utilization_percentage <= 70:
            return 60
        else:
            return 40


class LoanEligibilityService:
    """Service for checking loan eligibility and calculating terms"""
    
    @staticmethod
    def check_eligibility(customer_id, loan_amount, interest_rate, tenure):
        """
        Check loan eligibility and return appropriate response
        """
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Calculate credit score
            credit_score = CreditScoreService.calculate_credit_score(customer)
            
            # Check if current EMIs exceed 50% of monthly salary
            current_emis = LoanEligibilityService._calculate_current_emis(customer)
            if current_emis > float(customer.monthly_salary) * 0.5:
                return LoanEligibilityService._create_eligibility_response(
                    customer_id, False, interest_rate, interest_rate, 
                    tenure, 0, "Current EMIs exceed 50% of monthly salary"
                )
            
            # Determine approval and interest rate based on credit score
            approval, corrected_interest_rate = LoanEligibilityService._determine_approval(
                credit_score, interest_rate
            )
            
            if not approval:
                return LoanEligibilityService._create_eligibility_response(
                    customer_id, False, interest_rate, corrected_interest_rate,
                    tenure, 0, "Loan not approved based on credit score"
                )
            
            # Calculate monthly installment
            monthly_installment = LoanEligibilityService._calculate_monthly_installment(
                loan_amount, corrected_interest_rate, tenure
            )
            
            return LoanEligibilityService._create_eligibility_response(
                customer_id, True, interest_rate, corrected_interest_rate,
                tenure, monthly_installment, "Loan approved"
            )
            
        except Customer.DoesNotExist:
            return LoanEligibilityService._create_eligibility_response(
                customer_id, False, interest_rate, interest_rate,
                tenure, 0, "Customer not found"
            )
        except Exception as e:
            return LoanEligibilityService._create_eligibility_response(
                customer_id, False, interest_rate, interest_rate,
                tenure, 0, f"Error processing request: {str(e)}"
            )
    
    @staticmethod
    def _calculate_current_emis(customer):
        """Calculate total current EMIs for customer"""
        active_loans = Loan.objects.filter(customer=customer, is_active=True)
        return sum(loan.monthly_repayment for loan in active_loans)
    
    @staticmethod
    def _determine_approval(credit_score, requested_interest_rate):
        """
        Determine loan approval and corrected interest rate based on credit score
        """
        if credit_score > 50:
            # Approve with any interest rate
            return True, requested_interest_rate
        elif 30 < credit_score <= 50:
            # Approve only if interest rate > 12%
            if requested_interest_rate > 12:
                return True, requested_interest_rate
            else:
                return True, 12.0
        elif 10 < credit_score <= 30:
            # Approve only if interest rate > 16%
            if requested_interest_rate > 16:
                return True, requested_interest_rate
            else:
                return True, 16.0
        else:
            # Don't approve any loans
            return False, requested_interest_rate
    
    @staticmethod
    def _calculate_monthly_installment(loan_amount, interest_rate, tenure):
        """Calculate monthly installment using compound interest formula"""
        if interest_rate <= 0 or tenure <= 0:
            return 0
        
        # Convert annual interest rate to monthly
        monthly_rate = float(interest_rate) / 100 / 12
        
        # Calculate EMI using compound interest formula
        principal = float(loan_amount)
        if monthly_rate == 0:
            return principal / tenure
        
        emi = principal * (monthly_rate * (1 + monthly_rate) ** tenure) / ((1 + monthly_rate) ** tenure - 1)
        return round(emi, 2)
    
    @staticmethod
    def _create_eligibility_response(customer_id, approval, interest_rate, 
                                   corrected_interest_rate, tenure, monthly_installment, message):
        """Create standardized eligibility response"""
        return {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_installment,
            'message': message
        }


class LoanCreationService:
    """Service for creating loans"""
    
    @staticmethod
    def create_loan(customer_id, loan_amount, interest_rate, tenure):
        """
        Create a new loan if eligible
        """
        try:
            # Check eligibility first
            eligibility = LoanEligibilityService.check_eligibility(
                customer_id, loan_amount, interest_rate, tenure
            )
            
            if not eligibility['approval']:
                return {
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': eligibility['message'],
                    'monthly_installment': 0
                }
            
            # Create the loan
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Calculate start and end dates
            start_date = timezone.now().date()
            end_date = start_date.replace(year=start_date.year + (tenure // 12))
            if tenure % 12 > 0:
                end_date = end_date.replace(month=end_date.month + (tenure % 12))
            
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=eligibility['corrected_interest_rate'],
                monthly_repayment=eligibility['monthly_installment'],
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan created successfully',
                'monthly_installment': eligibility['monthly_installment']
            }
            
        except Customer.DoesNotExist:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Customer not found',
                'monthly_installment': 0
            }
        except Exception as e:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': f'Error creating loan: {str(e)}',
                'monthly_installment': 0
            } 