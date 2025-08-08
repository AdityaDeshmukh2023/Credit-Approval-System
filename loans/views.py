from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Customer, Loan
from .serializers import (
    CustomerRegistrationSerializer,
    LoanEligibilitySerializer,
    LoanEligibilityResponseSerializer,
    LoanCreateSerializer,
    LoanCreateResponseSerializer,
    LoanDetailSerializer,
    CustomerLoanSerializer
)
from .services import LoanEligibilityService, LoanCreationService


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer
    POST /api/register
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                customer = serializer.save()
                response_serializer = CustomerRegistrationSerializer(customer)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Error creating customer: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility for a customer
    POST /api/check-eligibility
    """
    serializer = LoanEligibilitySerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        eligibility_result = LoanEligibilityService.check_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        
        response_serializer = LoanEligibilityResponseSerializer(data=eligibility_result)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Error serializing response'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_loan(request):
    """
    Create a new loan for a customer
    POST /api/create-loan
    """
    serializer = LoanCreateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        loan_result = LoanCreationService.create_loan(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        
        response_serializer = LoanCreateResponseSerializer(data=loan_result)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Error serializing response'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details by loan ID
    GET /api/view-loan/{loan_id}
    """
    try:
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error retrieving loan: {str(e)}'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    View all loans for a customer
    GET /api/view-loans/{customer_id}
    """
    try:
        # Check if customer exists
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        serializer = CustomerLoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error retrieving customer loans: {str(e)}'}, 
            status=status.HTTP_404_NOT_FOUND
        ) 