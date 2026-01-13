from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import datetime, timedelta
from employee.models import Employee, DynamicField

class Command(BaseCommand):
    help = 'Generate fake employee data'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of employees to create')

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        
        # Create some dynamic fields if they don't exist
        fields_config = [
            {'label': 'Full Name', 'field_type': 'text'},
            {'label': 'Email', 'field_type': 'text'},
            {'label': 'Phone', 'field_type': 'text'},
            {'label': 'Address', 'field_type': 'text'},
            {'label': 'Date of Birth', 'field_type': 'date'},
            {'label': 'Salary', 'field_type': 'number'},
            {'label': 'Department', 'field_type': 'text'},
            {'label': 'Position', 'field_type': 'text'},
            {'label': 'Employment Date', 'field_type': 'date'},
            {'label': 'Emergency Contact', 'field_type': 'text'},
        ]

        # Create or update dynamic fields
        for i, field_data in enumerate(fields_config):
            DynamicField.objects.update_or_create(
                label=field_data['label'],
                defaults={
                    'field_type': field_data['field_type'],
                    'order': i
                }
            )

        departments = ['HR', 'Engineering', 'Marketing', 'Finance', 'Operations', 'Sales']
        positions = {
            'HR': ['HR Manager', 'Recruiter', 'HR Generalist'],
            'Engineering': ['Senior Developer', 'Junior Developer', 'Team Lead', 'Architect'],
            'Marketing': ['Marketing Manager', 'Content Writer', 'SEO Specialist'],
            'Finance': ['Accountant', 'Financial Analyst', 'CFO'],
            'Operations': ['Operations Manager', 'Logistics Coordinator'],
            'Sales': ['Sales Executive', 'Account Manager', 'Sales Director']
        }

        for _ in range(count):
            # Generate employee data
            department = random.choice(departments)
            position = random.choice(positions[department])
            employment_date = fake.date_between(start_date='-10y', end_date='today')
            
            employee_data = {
                'Full Name': fake.name(),
                'Email': fake.unique.email(),
                'Phone': fake.phone_number(),
                'Address': fake.address().replace('\n', ', '),
                'Date of Birth': fake.date_of_birth(minimum_age=22, maximum_age=60).strftime('%Y-%m-%d'),
                'Salary': random.randint(30000, 120000),
                'Department': department,
                'Position': position,
                'Employment Date': employment_date.strftime('%Y-%m-%d'),
                'Emergency Contact': f"{fake.name()} - {fake.phone_number()}",
            }

            # Create employee with the generated data
            Employee.objects.create(data=employee_data)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} fake employees'))
