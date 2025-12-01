from django.db import models


class DynamicField(models.Model):
    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("password", "Password"),
    ]

    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=100, choices=FIELD_TYPES)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.label

class Employee(models.Model):
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.data)
    