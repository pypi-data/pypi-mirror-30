import json


def get_base_dashboard():
    return json.dumps({
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": "-- Grafana --",
                    "enable": true,
                    "hide": true,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard"
                }
            ]
        },
        "editable": true,
        "gnetId": null,
        "graphTooltip": 0,
        "id": 6,
        "links": [],
        "panels": [
            {
                "aliasColors": {},
                "bars": false,
                "dashLength": 10,
                "dashes": false,
                "datasource": "bachend_siscorvac",
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
                    "alignAsTable": true,
                    "avg": true,
                    "current": true,
                    "hideEmpty": true,
                    "hideZero": false,
                    "max": true,
                    "min": true,
                    "show": true,
                    "total": false,
                    "values": true
                },
                "lines": true,
                "linewidth": 1,
                "links": [],
                "nullPointMode": "null",
                "percentage": false,
                "pointradius": 2,
                "points": true,
                "renderer": "flot",
                "seriesOverrides": [],
                "spaceLength": 10,
                "stack": false,
                "steppedLine": false,
                "targets": [
                    {
                        "$$hashKey": "object:672",
                        "alias": "",
                        "format": "time_series",
                        "rawSql": "SELECT\n  $__time(date),\n  value \nFROM\n  sensors_data_fibersensor\nWHERE\n  $__timeFilter(date) and\n  fiber_sensor_id = 1 and\n  variable_id = 185\n\n",
                        "refId": "B"
                    }
                ],
                "thresholds": [],
                "timeFrom": true,
                "timeShift": true,
                "title": "Humedad sector Malla",
                "tooltip": {
                    "shared": true,
                    "sort": 0,
                    "value_type": "individual"
                },
                "type": "graph",
                "xaxis": {
                    "buckets": true,
                    "mode": "time",
                    "name": true,
                    "show": true,
                    "values": []
                },
                "yaxes": [
                    {
                        "format": "percent",
                        "label": true,
                        "logBase": 1,
                        "max": true,
                        "min": true,
                        "show": true
                    },
                    {
                        "format": "short",
                        "label": true,
                        "logBase": 1,
                        "max": true,
                        "min": true,
                        "show": true
                    }
                ]
            },
            {
                "aliasColors": {},
                "bars": false,
                "dashLength": 10,
                "dashes": false,
                "datasource": "${DS_BACHEND_SISCORVAC}",
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
                    "alignAsTable": true,
                    "avg": true,
                    "current": true,
                    "hideEmpty": true,
                    "hideZero": false,
                    "max": true,
                    "min": true,
                    "show": true,
                    "total": false,
                    "values": true
                },
                "lines": true,
                "linewidth": 1,
                "links": [],
                "nullPointMode": "null",
                "percentage": false,
                "pointradius": 2,
                "points": true,
                "renderer": "flot",
                "seriesOverrides": [],
                "spaceLength": 10,
                "stack": false,
                "steppedLine": false,
                "targets": [
                    {
                        "alias": "",
                        "format": "time_series",
                        "rawSql": "SELECT $__time(date), value AS \"Conductividad electrica\" from sensors_data_fiber_sensor WHERE fiber_sensor_id = 2AND variable_id = Conductividad eléctrica fibra;",
                        "refId": "A"
                    }
                ],
                "thresholds": [],
                "timeFrom": true,
                "timeShift": true,
                "title": "Conductividad electrica Malla",
                "tooltip": {
                    "shared": true,
                    "sort": 0,
                    "value_type": "individual"
                },
                "type": "graph",
                "xaxis": {
                    "buckets": true,
                    "mode": "time",
                    "name": true,
                    "show": true,
                    "values": []
                },
                "yaxes": [
                    {
                        "format": "dS/m",
                        "label": true,
                        "logBase": 1,
                        "max": true,
                        "min": true,
                        "show": true
                    },
                    {
                        "format": "short",
                        "label": true,
                        "logBase": 1,
                        "max": true,
                        "min": true,
                        "show": true
                    }
                ]
            },
            {
                "aliasColors": {},
                "bars": false,
                "dashLength": 10,
                "dashes": false,
                "datasource": "${DS_BACHEND_SISCORVAC}",
                "decimals": 3,
                "fill": 1,
                "gridPos": {
                    "h": 9,
                    "w": 12,
                    "x": 0,
                    "y": 18
                },
                "id": 4,
                "legend": {
                    "alignAsTable": true,
                    "avg": true,
                    "current": true,
                    "hideEmpty": true,
                    "hideZero": false,
                    "max": true,
                    "min": true,
                    "show": true,
                    "total": false,
                    "values": true
                },
                "lines": true,
                "linewidth": 1,
                "links": [],
                "nullPointMode": "null",
                "percentage": false,
                "pointradius": 2,
                "points": true,
                "renderer": "flot",
                "seriesOverrides": [],
                "spaceLength": 10,
                "stack": false,
                "steppedLine": false,
                "targets": [
                    {
                        "alias": "",
                        "format": "time_series",
                        "rawSql": "SELECT $__time(date), value AS \"Temperatura\" from sensors_data_fiber_sensor WHERE fiber_sensor_id = 2AND variable_id = Temperatura fibra;",
                        "refId": "A"
                    }
                ],
                "thresholds": [],
                "timeFrom": true,
                "timeShift": true,
                "title": "Temperatura Malla",
                "tooltip": {
                    "shared": true,
                    "sort": 0,
                    "value_type": "individual"
                },
                "type": "graph",
                "xaxis": {
                    "buckets": true,
                    "mode": "time",
                    "name": true,
                    "show": true,
                    "values": []
                },
                "yaxes": [
                    {
                        "format": "celsius",
                        "label": true,
                        "logBase": 1,
                        "max": true,
                        "min": true,
                        "show": true
                    },
                    {
                        "format": "short",
                        "label": true,
                        "logBase": 1,
                        "max": true,
                        "min": true,
                        "show": true
                    }
                ]
            }
        ],
        "refresh": "5s",
        "schemaVersion": 16,
        "style": "dark",
        "tags": [],
        "templating": {
            "list": []
        },
        "time": {
            "from": "now-24h",
            "to": "now"
        },
        "timepicker": {
            "refresh_intervals": [
                "5s",
                "10s",
                "30s",
                "1m",
                "5m",
                "15m",
                "30m",
                "1h",
                "2h",
                "1d"
            ],
            "time_options": [
                "5m",
                "15m",
                "1h",
                "6h",
                "12h",
                "24h",
                "2d",
                "7d",
                "30d"
            ]
        },
        "timezone": "",
        "title": "SISCORVAC CREADO POR API",
        "uid": None,
        "version": 3
    })
