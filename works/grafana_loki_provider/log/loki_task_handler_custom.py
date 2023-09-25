"""Loki logging handler for tasks"""
import logging
import warnings
from typing import Dict
from typing import Optional
from typing import Type

import logging

logging.raiseExceptions = True

from logging_loki import const
from logging_loki import emitter
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.log.file_task_handler import FileTaskHandler
from typing import Any, Dict, Optional
import os

DEFAULT_LOGGER_NAME = "airflow"

logger = logging.getLogger(__name__)

class LokiHandler(FileTaskHandler, LoggingMixin):
    """
    Log handler that sends log records to Loki.

    `Loki API <https://github.com/grafana/loki/blob/master/docs/api.md>`_
    """

    emitters: Dict[str, Type[emitter.LokiEmitter]] = {
        "0": emitter.LokiEmitterV0,
        "1": emitter.LokiEmitterV1,
    }

    def __init__(
        self,
        url: str,
        base_log_folder: str,
        tags: Optional[dict] = None,
        auth: Optional[emitter.BasicAuth] = None,
        version: Optional[str] = None,
    ):
        """
        Create new Loki logging handler.

        Arguments:
            url: Endpoint used to send log entries to Loki (e.g. `https://my-loki-instance/loki/api/v1/push`).
            tags: Default tags added to every log record.
            auth: Optional tuple with username and password for basic HTTP authentication.
            version: Version of Loki emitter to use.

        """
        super().__init__(base_log_folder=base_log_folder)
        self.handler: logging.Handler | None = None
        self.labels: Dict[str, str] = {}
        self.extras: Dict[str, Any] = {}
        self.local_base = base_log_folder
        self.log_relative_path = ""

        if version is None and const.emitter_ver == "0":
            msg = (
                "Loki /api/prom/push endpoint is in the depreciation process starting from version 0.4.0.",
                "Explicitly set the emitter version to '0' if you want to use the old endpoint.",
                "Or specify '1' if you have Loki version> = 0.4.0.",
                "When the old API is removed from Loki, the handler will use the new version by default.",
            )
            warnings.warn(" ".join(msg), DeprecationWarning)

        version = version or const.emitter_ver
        if version not in self.emitters:
            raise ValueError("Unknown emitter version: {0}".format(version))
        self.emitter = self.emitters[version](url, tags, auth)

    def get_extras(self, ti, try_number=None) -> Dict[str, Any]:

        return dict(
            run_id=getattr(ti, "run_id", ""),
            try_number=try_number if try_number != None else ti.try_number,
            map_index=getattr(ti, "map_index", ""),
        )

    def get_labels(self, ti) -> Dict[str, str]:

        return {"dag_id": ti.dag_id, "task_id": ti.task_id}
    
    def set_context(self, task_instance) -> None:
        super().set_context(task_instance)
        logger.info(f"{task_instance}")
        

    def handleError(self, record):  # noqa: N802
        """Close emitter and let default handler take actions on error."""
        self.emitter.close()
        super().handleError(record)

    def emit(self, record: logging.LogRecord):
        """Send log record to Loki."""
        # noinspection PyBroadException
        try:
            self.emitter(record, self.format(record))
        except Exception:
            self.handleError(record)