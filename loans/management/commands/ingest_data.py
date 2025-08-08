from django.core.management.base import BaseCommand
from loans.tasks import ingest_all_data


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write('Starting data ingestion...')
        
        try:
            result = ingest_all_data()  # Synchronous call, not .delay()
            
            
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS('Data ingestion completed successfully!')
                )
                self.stdout.write(f"Customer result: {result['customer_result']}")
                self.stdout.write(f"Loan result: {result['loan_result']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'Data ingestion failed: {result["message"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during data ingestion: {str(e)}')
            ) 