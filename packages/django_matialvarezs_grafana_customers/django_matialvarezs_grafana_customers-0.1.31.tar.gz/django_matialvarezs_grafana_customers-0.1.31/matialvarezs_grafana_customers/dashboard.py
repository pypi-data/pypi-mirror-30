import json
from . import base_dashboard
def create_dashboard(panels):
    base = json.loads(base_dashboard.get_base_dashboard())
    base['panels'] = panels
    #for panel in panels:
    #    base['panels'].append(panel)
    return base