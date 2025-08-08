#!/usr/bin/env python3
"""
Test script for the Credit Approval System API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_register_customer():
    """Test customer registration"""
    print("Testing customer registration...")
    
    customer_data = {
        "first_name": "Aditya Deshmukh",
        "last_name": "Deshmukh",
        "age": 20,
        "monthly_income": 100000,
        "phone_number": 9876544210
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=customer_data)
        if response.status_code == 201:
            customer = response.json()
            print(f"✅ Customer registered successfully: {customer}")
            return customer['customer_id']
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def test_check_eligibility(customer_id):
    """Test loan eligibility check"""
    print(f"\nTesting loan eligibility for customer {customer_id}...")
    
    eligibility_data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    try:
        response = requests.post(f"{BASE_URL}/check-eligibility", json=eligibility_data)
        if response.status_code == 200:
            eligibility = response.json()
            print(f"✅ Eligibility check successful: {eligibility}")
            return eligibility['approval']
        else:
            print(f"❌ Eligibility check failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during eligibility check: {e}")
        return False

def test_create_loan(customer_id):
    """Test loan creation"""
    print(f"\nTesting loan creation for customer {customer_id}...")
    
    loan_data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    try:
        response = requests.post(f"{BASE_URL}/create-loan", json=loan_data)
        if response.status_code == 201:
            loan = response.json()
            print(f"✅ Loan created successfully: {loan}")
            return loan.get('loan_id')
        else:
            print(f"❌ Loan creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during loan creation: {e}")
        return None

def test_view_loan(loan_id):
    """Test viewing loan details"""
    print(f"\nTesting view loan details for loan {loan_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
        if response.status_code == 200:
            loan_details = response.json()
            print(f"✅ Loan details retrieved successfully: {loan_details}")
            return True
        else:
            print(f"❌ View loan failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error viewing loan: {e}")
        return False

def test_view_customer_loans(customer_id):
    """Test viewing customer loans"""
    print(f"\nTesting view customer loans for customer {customer_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
        if response.status_code == 200:
            customer_loans = response.json()
            print(f"✅ Customer loans retrieved successfully: {customer_loans}")
            return True
        else:
            print(f"❌ View customer loans failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error viewing customer loans: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")
    
    # Test with non-existent customer
    print("Testing with non-existent customer...")
    try:
        response = requests.post(f"{BASE_URL}/check-eligibility", json={
            "customer_id": 99999,
            "loan_amount": 100000,
            "interest_rate": 10.5,
            "tenure": 12
        })
        if response.status_code == 404:
            print("✅ Correctly handled non-existent customer")
        else:
            print(f"❌ Unexpected response for non-existent customer: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing non-existent customer: {e}")
    
    # Test with invalid data
    print("Testing with invalid data...")
    try:
        response = requests.post(f"{BASE_URL}/register", json={
            "first_name": "John",
            "last_name": "Doe",
            "age": 15,  # Invalid age
            "monthly_income": -1000,  # Invalid income
            "phone_number": "invalid"  # Invalid phone
        })
        if response.status_code == 400:
            print("✅ Correctly handled invalid data")
        else:
            print(f"❌ Unexpected response for invalid data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid data: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Credit Approval System API Tests")
    print("=" * 50)
    
    # Wait for API to be ready
    print("Waiting for API to be ready...")
    time.sleep(5)
    
    # Test customer registration
    customer_id = test_register_customer()
    if not customer_id:
        print("❌ Cannot proceed without customer registration")
        return
    
    # Test loan eligibility
    is_eligible = test_check_eligibility(customer_id)
    
    # Test loan creation if eligible
    loan_id = None
    if is_eligible:
        loan_id = test_create_loan(customer_id)
    
    # Test viewing loan details
    if loan_id:
        test_view_loan(loan_id)
    
    # Test viewing customer loans
    test_view_customer_loans(customer_id)
    
    # Test edge cases
    test_edge_cases()
    
    print("\n" + "=" * 50)
    print("🏁 API Tests Completed!")

if __name__ == "__main__":
    main() 