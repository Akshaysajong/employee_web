from django.http import JsonResponse
from django.shortcuts import render, redirect
from . models import *
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q


@login_required
def dashboard(request):
    """Dashboard view showing important metrics and recent activities"""
    total_employees = Employee.objects.count()
    total_fields = DynamicField.objects.all()
    recent_employees = Employee.objects.order_by('-created_at')[:5]

    recent_employees_list = []

    for emp in recent_employees:
        clean = {
            "id": emp.id,
            "data": [],
        }

        for field in total_fields:
            value = emp.data.get(field.label, "")
            clean["data"].append(value)

        recent_employees_list.append(clean)
    
    context = {
        'total_employees': total_employees,
        'total_fields': total_fields.count(),
        'dynamic_fields': total_fields,
        'recent_employees_list': recent_employees_list,
    }
    return render(request, 'dashboard.html', context)

@login_required
def form_builder(request):
    fields = DynamicField.objects.order_by('order')
    context = {
        "fields": fields,
    }
    return render (request, "form_builder.html", context)

@login_required
@csrf_exempt
def save_dynamic_field(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print('data:', data)
        label = data.get("label")
        field_type = data.get("field_type")
        order = data.get("order", 0)

        field = DynamicField.objects.create(
            label=label,
            field_type=field_type,
            order=order
        )
        return JsonResponse({"status": "success", "id": field.id})

    return JsonResponse({"error": "Invalid method"}, status=400)

@login_required
@csrf_exempt
def delete_field(request, id):
    if request.method == "DELETE":
        field = get_object_or_404(DynamicField, id=id)
        field.delete()
        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid method"}, status=400)


@login_required
def create_employee(request):
    fields = DynamicField.objects.order_by("order")
    print('fields:', fields)
    return render(request, "create_employee.html", {"fields": fields})

@login_required
@csrf_exempt
def save_employee(request):
    if request.method == "POST":
        try:
            # Parse the form data
            data = {}
            has_errors = False
            error_messages = []
            
            # Get all required fields
            required_fields = DynamicField.objects.filter(required=True).values_list('label', flat=True)
            
            # Process regular form fields
            for key, value in request.POST.items():
                if key != 'csrfmiddlewaretoken':  # Skip CSRF token
                    if not value.strip() and key in required_fields:
                        has_errors = True
                        error_messages.append(f"{key} is required")
                    data[key] = value.strip()
            
            # Handle file uploads if any
            if request.FILES:
                for key, file in request.FILES.items():
                    data[key] = file
            
            # Check if any required fields are missing
            missing_fields = [field for field in required_fields if field not in data or not str(data[field]).strip()]
            if missing_fields:
                has_errors = True
                error_messages.extend([f"{field} is required" for field in missing_fields])
            
            if has_errors:
                messages.error(request, 'Please fill in all required fields.')
                return JsonResponse({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': error_messages
                }, status=400)
            
            print('Received employee data:', data)  # Debug log
            
            # Create a new employee with the form data
            employee = Employee.objects.create(data=data)
        
            # Return success response
            messages.success(request, 'Employee created successfully!')
            return JsonResponse({
                'status': 'success',
                'message': 'Employee created successfully!',
                'redirect': '/create-employee/'
            })
            
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid form data"}, 
                status=400
            )
        except Exception as e:
            print(f"Error saving employee: {str(e)}")  # Debug log
            return JsonResponse(
                {"status": "error", "message": str(e)}, 
                status=500
            )
    
    return JsonResponse(
        {"status": "error", "message": "Method not allowed"}, 
        status=405
    )


@login_required
def list_employees(request):
    # Get search query
    q = request.GET.get("q", "").strip()
    
    # Get page number, default to 1
    page_number = request.GET.get('page', 1)
    
    # Get dynamic fields once
    dynamic_fields = DynamicField.objects.order_by("order").only('label', 'order')
    
    # Base queryset with only necessary fields
    employees = Employee.objects.only('id', 'data').order_by('-id')
    
    # Apply search filter if query exists
    if q:
        # Create a list of Q objects for each field
        q_objects = Q()
        for field in dynamic_fields:
            q_objects |= Q(data__has_key=field.label) & Q(data__icontains=q)
        employees = employees.filter(q_objects)
    
    # Paginate the results
    paginator = Paginator(employees, 50)  # Show 50 items per page
    page_obj = paginator.get_page(page_number)
    
    # Process only the current page of employees
    # processed_employees = []
    # for emp in page_obj:
    #     clean = {
    #         "id": emp.id,
    #         "data": [emp.data.get(field.label, "") for field in dynamic_fields]
    #     }
    #     processed_employees.append(clean)

    processed_employees = tuple(
        {
            "id": emp.id,
            "data": tuple(emp.data.get(field.label, "") for field in dynamic_fields)  # Also made data a tuple
        } 
        for emp in page_obj
    )
    
    return render(request, "employee_list.html", {
        "employees": processed_employees,
        "dynamic_fields": dynamic_fields,
        "page_obj": page_obj,
        "search_query": q,
    })

@login_required
@csrf_exempt
def delete_employees(request, id):
    emp = get_object_or_404(Employee, id=id)
    emp.delete()
    return JsonResponse({"status": "success"})