from . import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
from . import models
import json

def create_organisation(customer_id, name):
    data = {
        "name": name
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'orgs',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res:
        print("res al guardar organisation en grafana",res)
        organisation_id = json.loads(res)['orgId']
        customer_org_grafana = models.CustomerOrganisationGrafana(customer=customer_id, organisation_id=organisation_id)
        customer_org_grafana.save()



def create_user():
    pass


def create_dashboard():
    pass
