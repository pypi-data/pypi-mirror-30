from django.db import models

# Create your models here.
from customers.models import Customer


class CustomerOrganisationGrafana(models.Model):
    customer = models.ForeignKey(Customer,related_name='organization_customer_grafana')
    organisation_id = models.IntegerField(default=0)