import json
from . import base_dashboard,api
def create_dashboard(title_dashboard,panels):
    dashboard = base_dashboard.get_dashboard(title_dashboard,panels)
    #base['panels'] = panels
    #for panel in panels:
    #    base['panels'].append(panel)
    print("DASHBOARD COMPLETO:   ",dashboard)
    api.create_dashboard(dashboard)
    #return base