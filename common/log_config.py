from copy import deepcopy
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG
from grafana_loki_provider.log.loki_task_handler_custom import LokiHandler

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)
LOGGING_CONFIG['handlers']['loki_handler'] = {
    'class': 'grafana_loki_provider.log.loki_task_handler_custom.LokiHandler',
    'formatter': 'airflow',
    'tags': {"app": "airflow"},
    "url": "http://172.16.14.15:3100/loki/api/v1/push",
    "version": "1",
    "base_log_folder": "/home/vagrant/airflow/logs"    }
LOGGING_CONFIG['root']['handlers'].append('loki_handler')
# print(LOGGING_CONFIG)