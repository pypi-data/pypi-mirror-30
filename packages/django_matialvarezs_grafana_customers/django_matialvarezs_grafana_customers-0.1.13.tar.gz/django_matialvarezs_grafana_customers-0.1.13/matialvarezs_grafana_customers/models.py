from django.db import models

# Create your models here.
from business.models import Business


class BusinessCustomerOrganisationGrafana(models.Model):
    business = models.ForeignKey(Business,related_name='organization_grafana_business_customer')
    organisation_id = models.IntegerField(default=0)