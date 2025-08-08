from rest_framework import serializers
from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    name = serializers.SerializerMethodField()
    monthly_income = serializers.DecimalField(source='monthly_salary', max_digits=12, decimal_places=2)

    class Meta:
        model = Customer
        fields = [
            'customer_id', 'name', 'age', 'monthly_income', 
            'approved_limit', 'phone_number'
        ]
        read_only_fields = ['customer_id', 'approved_limit']

    def get_name(self, obj):
        return obj.full_name


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer registration"""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18, max_value=100)
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    phone_number = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

    def create(self, validated_data):
        # Map monthly_income to monthly_salary
        validated_data['monthly_salary'] = validated_data.pop('monthly_income')
        return super().create(validated_data)

    def to_representation(self, instance):
        """Custom representation for registration response"""
        return {
            'customer_id': instance.customer_id,
            'name': instance.full_name,
            'age': instance.age,
            'monthly_income': instance.monthly_salary,
            'approved_limit': instance.approved_limit,
            'phone_number': instance.phone_number
        }


class LoanEligibilitySerializer(serializers.Serializer):
    """Serializer for loan eligibility check"""
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1, max_value=60)


class LoanEligibilityResponseSerializer(serializers.Serializer):
    """Serializer for loan eligibility response"""
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class LoanCreateSerializer(serializers.Serializer):
    """Serializer for loan creation"""
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1, max_value=60)


class LoanCreateResponseSerializer(serializers.Serializer):
    """Serializer for loan creation response"""
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Serializer for customer details in loan view"""
    id = serializers.IntegerField(source='customer_id')
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.IntegerField()
    age = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']


class LoanDetailSerializer(serializers.ModelSerializer):
    """Serializer for loan details"""
    customer = CustomerDetailSerializer()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=12, decimal_places=2)
    tenure = serializers.IntegerField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']


class CustomerLoanSerializer(serializers.ModelSerializer):
    """Serializer for customer loans list"""
    loan_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=12, decimal_places=2)
    repayments_left = serializers.IntegerField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left'] 