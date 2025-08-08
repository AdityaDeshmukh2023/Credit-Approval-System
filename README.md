# Credit Approval System

A Django REST API-based credit approval system that processes loan applications based on customer credit scores and historical data.

## Features

- **Customer Registration**: Register new customers with automatic approved limit calculation
- **Loan Eligibility Check**: Check loan eligibility based on credit score and business rules
- **Loan Creation**: Create loans for eligible customers
- **Loan Management**: View loan details and customer loan history
- **Background Data Processing**: Celery-based background tasks for data ingestion
- **Credit Scoring**: Comprehensive credit score calculation based on historical data
- **Docker Support**: Complete containerization with Docker Compose

## Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: PostgreSQL 15
- **Task Queue**: Celery + Redis
- **Containerization**: Docker + Docker Compose
- **Data Processing**: Pandas + OpenPyXL

## API Endpoints

### 1. Register Customer
- **POST** `/api/register`
- **Request Body**:
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
  }
  ```
- **Response**:
  ```json
  {
    "customer_id": 1,
    "name": "John Doe",
    "age": 30,
    "monthly_income": 50000,
    "approved_limit": 1800000,
    "phone_number": 9876543210
  }
  ```

### 2. Check Loan Eligibility
- **POST** `/api/check-eligibility`
- **Request Body**:
  ```json
  {
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "tenure": 12
  }
  ```
- **Response**:
  ```json
  {
    "customer_id": 1,
    "approval": true,
    "interest_rate": 10.5,
    "corrected_interest_rate": 10.5,
    "tenure": 12,
    "monthly_installment": 8791.67
  }
  ```

### 3. Create Loan
- **POST** `/api/create-loan`
- **Request Body**:
  ```json
  {
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "tenure": 12
  }
  ```
- **Response**:
  ```json
  {
    "loan_id": 1,
    "customer_id": 1,
    "loan_approved": true,
    "message": "Loan created successfully",
    "monthly_installment": 8791.67
  }
  ```

### 4. View Loan Details
- **GET** `/api/view-loan/{loan_id}`
- **Response**:
  ```json
  {
    "loan_id": 1,
    "customer": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": 9876543210,
      "age": 30
    },
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "monthly_installment": 8791.67,
    "tenure": 12
  }
  ```

### 5. View Customer Loans
- **GET** `/api/view-loans/{customer_id}`
- **Response**:
  ```json
  [
    {
      "loan_id": 1,
      "loan_amount": 100000,
      "interest_rate": 10.5,
      "monthly_installment": 8791.67,
      "repayments_left": 8
    }
  ]
  ```

## Credit Scoring Algorithm

The system calculates credit scores (0-100) based on:

1. **Past Loans Paid on Time** (40% weight)
   - Percentage of EMIs paid on time vs total EMIs

2. **Number of Loans Taken** (20% weight)
   - More loans = higher score (up to 5+ loans)

3. **Loan Activity in Current Year** (20% weight)
   - Active loans in current year = higher score

4. **Loan Approved Volume** (20% weight)
   - Utilization percentage of approved limit

## Loan Approval Rules

- **Credit Score > 50**: Approve with any interest rate
- **Credit Score 30-50**: Approve only if interest rate > 12%
- **Credit Score 10-30**: Approve only if interest rate > 16%
- **Credit Score < 10**: No loans approved
- **Current EMIs > 50% of monthly salary**: No loans approved

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Excel files: `customer_data.xlsx` and `loan_data.xlsx` in the project root

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd credit-approval-system
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Ingest initial data** (in a new terminal)
   ```bash
   docker-compose exec web python manage.py ingest_data
   ```

4. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

### Manual Setup (without Docker)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   ```bash
   # Create database and user
   createdb credit_approval_db
   ```

3. **Configure environment variables**
   ```bash
   export POSTGRES_DB=credit_approval_db
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=postgres
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export REDIS_URL=redis://localhost:6379/0
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Redis server**
   ```bash
   redis-server
   ```

6. **Start Celery worker** (in a new terminal)
   ```bash
   celery -A credit_approval_system worker -l info
   ```

7. **Start the application**
   ```bash
   python manage.py runserver
   ```

8. **Ingest data**
   ```bash
   python manage.py ingest_data
   ```

## Project Structure

```
credit-approval-system/
├── credit_approval_system/     # Django project settings
├── loans/                      # Main application
│   ├── models.py              # Data models
│   ├── serializers.py         # API serializers
│   ├── views.py               # API views
│   ├── services.py            # Business logic
│   ├── tasks.py               # Celery tasks
│   ├── admin.py               # Django admin
│   └── management/            # Management commands
├── customer_data.xlsx         # Customer data file
├── loan_data.xlsx            # Loan data file
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md               # This file
```

## Testing the API

### Using curl

1. **Register a customer**
   ```bash
   curl -X POST http://localhost:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "John",
       "last_name": "Doe",
       "age": 30,
       "monthly_income": 50000,
       "phone_number": 9876543210
     }'
   ```

2. **Check loan eligibility**
   ```bash
   curl -X POST http://localhost:8000/api/check-eligibility \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": 1,
       "loan_amount": 100000,
       "interest_rate": 10.5,
       "tenure": 12
     }'
   ```

3. **Create a loan**
   ```bash
   curl -X POST http://localhost:8000/api/create-loan \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": 1,
       "loan_amount": 100000,
       "interest_rate": 10.5,
       "tenure": 12
     }'
   ```

### Using Python requests

```python
import requests

# Register customer
response = requests.post('http://localhost:8000/api/register', json={
    'first_name': 'John',
    'last_name': 'Doe',
    'age': 30,
    'monthly_income': 50000,
    'phone_number': 9876543210
})
customer = response.json()

# Check eligibility
response = requests.post('http://localhost:8000/api/check-eligibility', json={
    'customer_id': customer['customer_id'],
    'loan_amount': 100000,
    'interest_rate': 10.5,
    'tenure': 12
})
eligibility = response.json()

# Create loan if eligible
if eligibility['approval']:
    response = requests.post('http://localhost:8000/api/create-loan', json={
        'customer_id': customer['customer_id'],
        'loan_amount': 100000,
        'interest_rate': 10.5,
        'tenure': 12
    })
    loan = response.json()
```

## Business Logic

### Approved Limit Calculation
- `approved_limit = 36 * monthly_salary` (rounded to nearest lakh)

### Monthly Installment Calculation
- Uses compound interest formula: EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
- Where P = principal, r = monthly interest rate, n = tenure in months

### Credit Score Components
1. **Payment History**: 40% weight
2. **Loan Count**: 20% weight  
3. **Current Year Activity**: 20% weight
4. **Loan Volume**: 20% weight

## Error Handling

The API includes comprehensive error handling for:
- Invalid input data
- Customer not found
- Loan not found
- Database errors
- Business rule violations

All errors return appropriate HTTP status codes and descriptive error messages.

## Performance Considerations

- Database queries are optimized with proper indexing
- Background tasks handle data ingestion asynchronously
- API responses are paginated for large datasets
- Caching can be easily added for frequently accessed data

## Security Features

- Input validation and sanitization
- SQL injection prevention through ORM
- CORS configuration for cross-origin requests
- Environment variable configuration for sensitive data

## Monitoring and Logging

- Django admin interface for data management
- Celery task monitoring
- Application logs for debugging
- Database query optimization

## Future Enhancements

- Unit and integration tests
- API documentation with Swagger/OpenAPI
- Rate limiting
- Authentication and authorization
- Advanced analytics and reporting
- Email notifications
- Mobile app support 


docker-compose exec web python manage.py ingest_data

python test_api.py