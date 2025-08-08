import pandas as pd
from celery import shared_task
from django.utils import timezone
from datetime import datetime, date
from .models import Customer, Loan


@shared_task
def ingest_customer_data():
    """
    Background task to ingest customer data from Excel file
    """
    try:
        # Read customer data from Excel
        df = pd.read_excel('customer_data.xlsx')
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            customer_data = {
                'customer_id': int(row['Customer ID']),
                'first_name': str(row['First Name']),
                'last_name': str(row['Last Name']),
                'phone_number': int(row['Phone Number']),
                'monthly_salary': float(row['Monthly Salary']),
                'approved_limit': float(row['Approved Limit']),
                'current_debt': 0.0,  # Default since not in original data
                'age': int(row['Age']),
            }
            
            # Try to get existing customer or create new one
            customer, created = Customer.objects.update_or_create(
                customer_id=customer_data['customer_id'],
                defaults=customer_data
            )
            
            if created:
                customers_created += 1
            else:
                customers_updated += 1
        
        return {
            'status': 'success',
            'message': f'Customer data ingested successfully. Created: {customers_created}, Updated: {customers_updated}',
            'customers_created': customers_created,
            'customers_updated': customers_updated
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error ingesting customer data: {str(e)}'
        }


@shared_task
def ingest_loan_data():
    """
    Background task to ingest loan data from Excel file
    """
    try:
        # Read loan data from Excel
        df = pd.read_excel('loan_data.xlsx')
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            try:
                # Get customer
                customer = Customer.objects.get(customer_id=int(row['Customer ID']))
                
                # Parse dates
                start_date = pd.to_datetime(row['Date of Approval']).date()
                end_date = pd.to_datetime(row['End Date']).date()
                
                loan_data = {
                    'loan_id': int(row['Loan ID']),
                    'customer': customer,
                    'loan_amount': float(row['Loan Amount']),
                    'tenure': int(row['Tenure']),
                    'interest_rate': float(row['Interest Rate']),
                    'monthly_repayment': float(row['Monthly payment']),
                    'emis_paid_on_time': int(row['EMIs paid on Time']),
                    'start_date': start_date,
                    'end_date': end_date,
                }
                
                # Try to get existing loan or create new one
                loan, created = Loan.objects.update_or_create(
                    loan_id=loan_data['loan_id'],
                    defaults=loan_data
                )
                
                if created:
                    loans_created += 1
                else:
                    loans_updated += 1
                    
            except Customer.DoesNotExist:
                print(f"Customer {row['Customer ID']} not found for loan {row['Loan ID']}")
                continue
            except Exception as e:
                print(f"Error processing loan {row['Loan ID']}: {str(e)}")
                continue
        
        return {
            'status': 'success',
            'message': f'Loan data ingested successfully. Created: {loans_created}, Updated: {loans_updated}',
            'loans_created': loans_created,
            'loans_updated': loans_updated
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error ingesting loan data: {str(e)}'
        }


@shared_task
def ingest_all_data():
    """
    Background task to ingest both customer and loan data
    """
    try:
        # Ingest customer data first
        customer_result = ingest_customer_data()
        # customer_result = customer_result.get()
        
        # Ingest loan data
        loan_result = ingest_loan_data()
        # loan_result = loan_result.get()
        
        return {
            'status': 'success',
            'customer_result': customer_result,
            'loan_result': loan_result,
            'message': 'All data ingested successfully'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error ingesting data: {str(e)}'
        } 