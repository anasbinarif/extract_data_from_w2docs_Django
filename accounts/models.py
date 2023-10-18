from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Employer(models.Model):
    employer_name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.employer_name


class Employee(models.Model):
    employee_name = models.CharField(max_length=254)
    social_security_number = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.employee_name


class TaxDetails(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    federal_income_tax_withheld = models.FloatField()
    wages_tips_and_compensation = models.FloatField()
    medicare_tax_withheld = models.FloatField()
    medicare_wages_and_tips = models.FloatField()
    social_security_tax_withheld = models.FloatField()
    social_security_wages = models.FloatField()
    tax_year = models.CharField(max_length=4)

    def __str__(self):
        return f'Tax Details for {self.employee} - {self.tax_year}'
