from django.db import models

# Create your models here.
#from business.models import Business


class BusinessCustomerOrganisationGrafana(models.Model):
    business = models.IntegerField(default=0)
    organisation_id = models.IntegerField(default=0)