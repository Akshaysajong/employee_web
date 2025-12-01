Employee Management System- Django

Employee Management System built with Django, featuring authentication, dynamic form builder, employee creation using customizable fields, search filters, and full REST API support using JWT authentication.

Authentication & User Profile

    1. Login
    2. Register
    3. Change Password
    4. User Profile (view/update)
    5. JWT-based authentication (Access + Refresh tokens)

Dynamic Form Builder
    Create forms to capture dynamic employee details.
    Add new fields dynamically:
        Text
        Number
        Date
        Password

Employee Management
    Employee Creation
        Employees are created using the pre-designed dynamic form
        List all employees
        Delete employee

API Documentation

Register API
    POST /api/register/

    Payload:
        {
        "username": "admin",
        "email": "admin@gmail.com",
        "password": "Admin123"
        }

Login 
    POST /api/login/

    Payload:
        {
        "username": "admin",
        "password": "Admin123"
        }

    Response:
        {
        "access": "jwt-access-token",
        "refresh": "jwt-refresh-token"
        }

Refresh Token
    POST /api/refresh/

    {
    "refresh": "your-refresh-token"
    }

Dynamic Form APIs

    Create Field
        POST /api/fields/

        Payload:
            {
                "label": "phone",
                "field_type": "number",
                "order": 2
            }
    
    List Fields
        GET /api/fields/

    Update Field
        PUT /api/fields/

        Payload:
            {
                "label": "phone",
                "field_type": "number",
                "order": 2
            }

    Delete Field
        DELETE api/fields/id/

Employee APIs

    Create Employee
        POST /api/employees/create/

        Payload:
            {
                "data": {
                    "name": "emp6",
                    "id": 6
                }
            }
    Get All Employees
        GET /api/employees/

    Update Employee
        PUT /api/employees/5/
        Payload:
            {
                "data": {
                    "name": "emp 4",
                    "id": 14
                    
                }
            }

    Delete Employee
        DELETE /api/employees/5/
