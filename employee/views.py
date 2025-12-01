from django.http import JsonResponse
from django.shortcuts import render, redirect
from . models import *
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


def form_builder(request):
    fields = DynamicField.objects.order_by('order')
    context = {
        "fields": fields,
    }
    return render (request, "form_builder.html", context)


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


@csrf_exempt
def delete_field(request, id):
    if request.method == "DELETE":
        field = get_object_or_404(DynamicField, id=id)
        field.delete()
        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid method"}, status=400)


def create_employee(request):
    fields = DynamicField.objects.order_by("order")
    return render(request, "create_employee.html", {"fields": fields})

@csrf_exempt
def save_employee(request):
    if request.method == "POST":
        data = json.loads(request.body)

        Employee.objects.create(data=data)
        return JsonResponse({"message": "Employee added successfully"})
    

def list_employees(request):
    q = request.GET.get("q", "")
    print('q:', q)
    employees = Employee.objects.all()
    dynamic_fields = DynamicField.objects.order_by("order")

    processed_employees = []

    for emp in employees:
        clean = {
            "id": emp.id,
            "data": [],
        }

        for field in dynamic_fields:
            value = emp.data.get(field.label, "")
            clean["data"].append(value)

        processed_employees.append(clean)

    return render(request, "employee_list.html", {
        "employees": processed_employees,
        "dynamic_fields": dynamic_fields,
    })


@csrf_exempt
def delete_employees(request, id):
    print('id:', id)
    emp = get_object_or_404(Employee, id=id)
    # emp.delete()
    return JsonResponse({"status": "success"})