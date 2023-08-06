import json

def create_dashboard(panels):
    base = json.load(open('./base_dashboard.json'))
    for panel in panels:
        base['panels'].append(panel)
    return base