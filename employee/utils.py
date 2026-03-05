import pandas as pd
from django.core.exceptions import ValidationError
from .models import Employee, DynamicField

def process_excel_file(file):
    """
    Process the uploaded Excel file and create Employee records.
    Returns a tuple of (success_count, error_count, errors)
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Get required fields from DynamicField
        required_fields = set(DynamicField.objects.filter(required=True).values_list('label', flat=True))
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Process each row in the Excel file
        for index, row in df.iterrows():
            try:
                # Convert row to dictionary and clean data
                row_data = row.to_dict()
                
                # Check for missing required fields
                missing_fields = required_fields - set(row_data.keys())
                if missing_fields:
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
                
                # Clean the data (remove NaN/None values)
                clean_data = {}
                clean_emp_data = {}
                for key, value in row_data.items():
                    if pd.isna(value):
                        clean_data[key] = ""
                        clean_emp_data[key] = ""
                    else:
                        # Convert numpy types to Python native types
                        if hasattr(value, 'item'):
                            clean_data[key] = value.item()
                            clean_emp_data[key] = value.item()
                        else:
                            clean_data[key] = value
                            clean_emp_data[key] = value
                
                # Create employee record with both data and emp_data fields
                employee = Employee.objects.create(
                    data=clean_data,
                    emp_data=clean_emp_data
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")
                
        return success_count, error_count, errors
        
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")
