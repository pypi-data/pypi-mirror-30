def get_panel_to_add_dashboard(title, query, format_unit_y_axes):
    return {
        "aliasColors": {},
        "bars": False,
        "dashLength": 10,
        "dashes": False,
        "datasource": "DS_BACHEND_SISCORVAC",
        "decimals": 3,
        "fill": 1,
        "gridPos": {
            "h": 9,
            "w": 12,
            "x": 0,
            "y": 9
        },
        "id": 4,
        "legend": {
            "alignAsTable": True,
            "avg": True,
            "current": True,
            "hideEmpty": True,
            "hideZero": False,
            "max": True,
            "min": True,
            "show": True,
            "total": False,
            "values": True
        },
        "lines": True,
        "linewidth": 1,
        "links": [],
        "nullPointMode": "null",
        "percentage": False,
        "pointradius": 2,
        "points": True,
        "renderer": "flot",
        "seriesOverrides": [],
        "spaceLength": 10,
        "stack": False,
        "steppedLine": False,
        "targets": [
            {
                "alias": "",
                "format": "time_series",
                "rawSql": query,
                "refId": "A"
            }
        ],
        "thresholds": [],
        "timeFrom": True,
        "timeShift": True,
        "title": title,
        "tooltip": {
            "shared": True,
            "sort": 0,
            "value_type": "individual"
        },
        "type": "graph",
        "xaxis": {
            "buckets": True,
            "mode": "time",
            "name": True,
            "show": True,
            "values": []
        },
        "yaxes": [
            {
                "format": format_unit_y_axes,
                "label": True,
                "logBase": 1,
                "max": True,
                "min": True,
                "show": True
            },
            {
                "format": "short",
                "label": True,
                "logBase": 1,
                "max": True,
                "min": True,
                "show": True
            }
        ]
    }
