from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
import uuid
from pathlib import Path
from typing import Union
import logging
import os

import petl as etl
from django.conf import settings
from django.db.models import Model

from core.retriever import SWAPIRetriever, SWAPIException

logger = logging.getLogger(__name__)


@dataclass
class ImporterConfig:
    endpoint: str
    model_class: Model
    data_folder: str
    dropped_fields: set


class SWAPIImporter(ABC):
    def __init__(self):
        self.retriever = SWAPIRetriever()

    @cached_property
    @abstractmethod
    def config(self) -> ImporterConfig:
        return ImporterConfig()

    def create_csv_file(self) -> Path:
        file_created = False
        headers = self.get_schema()
        while file_created is False:
            path = Path(
                settings.MEDIA_ROOT
                / self.config.data_folder
                / f"{uuid.uuid4().hex}.csv"
            )
            try:
                with path.open(mode="x") as csv_file:
                    csv_file.write(str(headers))
                    csv_file.write("\n")
                    file_created = True
            except FileExistsError:
                pass
        return path

    def get_schema(self):
        try:
            schema = self.retriever.retrieve_one(f"{self.config.endpoint}/schema").get(
                "properties", {}
            )
        except SWAPIException:
            # Some existing SWAPI instances have troubles with schema endpoint
            schema = self.retriever.retrieve_one(f"{self.config.endpoint}/1")
        fields = {str(field) for field in schema.keys()}
        return sorted(list(fields.difference(self.config.dropped_fields)))

    @abstractmethod
    def transform_data(self, data):
        return NotImplementedError

    def import_data(self) -> Union[None, Model]:
        try:
            path = self.create_csv_file()
            for source_data in self.retriever.retrieve_all(self.config.endpoint):
                etl_data = etl.fromdicts(source_data)
                self.transform_data(etl_data).appendcsv(path)
            db_file = self.config.model_class()
            db_file.file.name = os.path.join(path.parts[1:])
            db_file.save()
            return db_file
        except SWAPIException as exc:
            logger.exception(exc)
            return None
