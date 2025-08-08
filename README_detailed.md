# Credit Approval System

This is a Django-based credit approval system that provides APIs for managing customer and loan data, checking loan eligibility, and creating new loans.

## Project Structure

```
.
├── credit_approval_system/  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── loans/                   # Django app for loan management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tasks.py
│   ├── urls.py
│   └── views.py
│   └── management/
│       └── commands/
│           ├── ingest_data.py
│           └── wait_for_db.py
├── customer_data.xlsx       # Sample customer data
├── loan_data.xlsx           # Sample loan data
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── start.sh                 # Script to start the application
└── README.md
```

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.8+
    *   Docker
    *   Docker Compose

2.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

3.  **Build and run with Docker:**
    ```bash
    docker-compose up --build
    ```
    This will start the Django application, a PostgreSQL database, and a Celery worker.

4.  **Ingest initial data:**
    Once the containers are running, open a new terminal and run the following command to load the initial customer and loan data from the provided Excel files:
    ```bash
    docker-compose exec web python manage.py ingest_data
    ```

## API Endpoints

The following are the available API endpoints.

### Register a new customer

*   **URL:** `/api/register/`
*   **Method:** `POST`
*   **Description:** Registers a new customer in the system.
*   **Request Body:**
    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "age": 25,
        "monthly_income": 5000,
        "phone_number": "1234567890"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
        "customer_id": 1,
        "name": "John Doe",
        "age": 25,
        "monthly_income": 5000,
        "approved_limit": 1800000,
        "phone_number": "1234567890"
    }
    ```

### Check loan eligibility

*   **URL:** `/api/check-eligibility/`
*   **Method:** `POST`
*   **Description:** Checks if a customer is eligible for a loan and provides details if they are.
*   **Request Body:**
    ```json
    {
        "customer_id": 1,
        "loan_amount": 100000,
        "interest_rate": 12.5,
        "tenure": 12
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "customer_id": 1,
        "approval": true,
        "interest_rate": 12.5,
        "corrected_interest_rate": 12.5,
        "tenure": 12,
        "monthly_installment": 9263.5
    }
    ```

### Create a new loan

*   **URL:** `/api/create-loan/`
*   **Method:** `POST`
*   **Description:** Creates a new loan for a customer if they are eligible.
*   **Request Body:**
    ```json
    {
        "customer_id": 1,
        "loan_amount": 100000,
        "interest_rate": 12.5,
        "tenure": 12
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
        "loan_id": 1,
        "customer_id": 1,
        "loan_approved": true,
        "message": "Loan approved",
        "monthly_installment": 9263.5
    }
    ```

### View loan details

*   **URL:** `/api/view-loan/<loan_id>/`
*   **Method:** `GET`
*   **Description:** Retrieves the details of a specific loan.
*   **Success Response (200 OK):**
    ```json
    {
        "loan_id": 1,
        "customer": {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1234567890",
            "age": 25
        },
        "loan_amount": "100000.00",
        "interest_rate": "12.50",
        "monthly_installment": "9263.50",
        "tenure": 12
    }
    ```

### View loans for a customer

*   **URL:** `/api/view-loans/<customer_id>/`
*   **Method:** `GET`
*   **Description:** Retrieves all loans for a specific customer.
*   **Success Response (200 OK):**
    ```json
    [
        {
            "loan_id": 1,
            "loan_amount": 100000,
            "interest_rate": 12.5,
            "monthly_payment": 9263.5,
            "repayments_left": 12
        }
    ]
    ```
