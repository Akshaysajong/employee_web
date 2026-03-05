import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

def generate_sample_employees(num_employees=100000):
    # Initialize Faker
    fake = Faker()

    # Generate fake employee data
    data = []
    for _ in range(num_employees):
        hire_date = fake.date_between(start_date='-5y', end_date='today')
        data.append({
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number()[:15],  # Limit phone number length
            'department': random.choice(['HR', 'Engineering', 'Marketing', 'Sales', 'Finance', 'IT']),
            'position': fake.job(),
            'salary': round(random.uniform(30000, 120000), 2),
            'hire_date': hire_date.strftime('%Y-%m-%d'),
            'address': fake.address().replace('\n', ', '),
            'city': fake.city(),
            'country': fake.country(),
            'postal_code': fake.postcode(),
            'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d'),
            'emergency_contact': fake.name(),
            'emergency_phone': fake.phone_number()[:15],
        })

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Reorder columns to put the most important fields first
    columns = [
        'first_name', 'last_name', 'email', 'phone', 'department', 'position',
        'salary', 'hire_date', 'date_of_birth', 'address', 'city', 'country',
        'postal_code', 'emergency_contact', 'emergency_phone'
    ]
    df = df[columns]

    # Save to Excel
    output_file = 'sample_employee_data.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')

    print(f"Sample Excel file created: {output_file}")
    print(f"Number of employees generated: {len(df)}")
    return output_file

if __name__ == "__main__":
    generate_sample_employees()