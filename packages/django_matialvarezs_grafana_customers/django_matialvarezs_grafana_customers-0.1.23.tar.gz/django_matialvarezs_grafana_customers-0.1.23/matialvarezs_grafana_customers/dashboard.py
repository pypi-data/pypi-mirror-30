import json
def create_dashboard(panels):
    base = json.dumps(open('base_dashboard.json'))
    for panel in panels:
        base['panels'].append(panel)