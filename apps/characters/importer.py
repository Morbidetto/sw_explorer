from functools import cached_property, lru_cache

from dateutil import parser

from core.importer import ImporterConfig, SWAPIImporter
from characters.models import CharactersCsvFile


class CharacterImporter(SWAPIImporter):
    @cached_property
    def config(self) -> ImporterConfig:
        return ImporterConfig(
            endpoint="people",
            model_class=CharactersCsvFile,
            data_folder="characters",
            dropped_fields={
                "films",
                "species",
                "vehicles",
                "starships",
                "created",
                "url",
            },
        )

    @lru_cache(maxsize=1024)
    def get_planet_name(self, swapi_url: str) -> str:
        planet_data = self.retriever.retrieve_one(swapi_url)
        return planet_data.get("name", "")

    @property
    def schema(self) -> list:
        schema = super().schema
        return [field if field != "edited" else "date" for field in schema]

    def transform_data(self, data):
        return (
            data.cutout(*self.config.dropped_fields)
            .rename("edited", "date")
            .convert(
                {
                    "date": lambda v: parser.parse(v).date(),
                    "homeworld": lambda v: self.get_planet_name(v),
                }
            )
            .sortheader()
        )
