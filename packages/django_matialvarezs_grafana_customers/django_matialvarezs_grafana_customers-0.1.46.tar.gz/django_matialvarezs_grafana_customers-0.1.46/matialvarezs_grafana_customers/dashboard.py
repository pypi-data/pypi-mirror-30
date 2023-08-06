import json
from . import base_dashboard,api
def create_dashboard(panels):
    base = json.loads(base_dashboard.get_base_dashboard())
    base['panels'] = panels
    #for panel in panels:
    #    base['panels'].append(panel)
    print("DASHBOARD COMPLETO:   ",base)
    api.create_dashboard(base)
    #return base