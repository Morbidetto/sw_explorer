from unittest import mock
from datetime import date

import pytest
import petl as etl
from django.http import Http404
from django.test import RequestFactory

from characters.models import CharactersCsvFile
from characters.importer import CharacterImporter
from characters.views import CharactersDetailView

class TestCharacterImporter:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.importer = CharacterImporter()
        self.importer.retriever = mock.MagicMock()
        self.planet_name = "Big planet"

    def test_schema_rules(self):
        headers = ["test", "test2", "atest", "edited"]
        self.importer.config.dropped_fields = ["test"]
        self.importer.retriever.retrieve_one.return_value = {
            "properties": {key: None for key in headers}
        }
        schema = self.importer.schema
        # 'test' removed and 'edited' transformed
        modifed_headers = ["test2", "atest", "date"]
        assert schema == sorted(modifed_headers)

    def test_getting_planet_name(self):
        self.importer.retriever.retrieve_one.return_value = {"name": self.planet_name}
        name = self.importer.get_planet_name("")
        assert name == self.planet_name
        self.importer.get_planet_name("2")

    def test_planet_names_cache(self):
        self.importer.get_planet_name("")
        assert 1 == self.importer.retriever.retrieve_one.call_count
        self.importer.get_planet_name("2")
        assert 2 == self.importer.retriever.retrieve_one.call_count
        self.importer.get_planet_name("2")
        assert 2 == self.importer.retriever.retrieve_one.call_count

    def test_data_transform(self):
        self.importer.get_planet_name = mock.MagicMock()
        self.importer.get_planet_name.return_value = self.planet_name
        table = [
            {
                "name": "Sly Moore",
                "height": "178",
                "mass": "48",
                "hair_color": "none",
                "skin_color": "pale",
                "eye_color": "white",
                "birth_year": "unknown",
                "gender": "female",
                "homeworld": "http://swapi:8000/api/planets/60/",
                "films": [
                    "http://swapi:8000/api/films/5/",
                    "http://swapi:8000/api/films/6/",
                ],
                "species": ["http://swapi:8000/api/species/1/"],
                "vehicles": [],
                "starships": [],
                "created": "2014-12-20T20:18:37.619000Z",
                "edited": "2014-12-20T21:17:50.496000Z",
                "url": "http://swapi:8000/api/people/82/",
            }
        ]
        table = etl.fromdicts(table)
        transformed_table = self.importer.transform_data(table)
        assert transformed_table.header() == (
            "birth_year",
            "date",
            "eye_color",
            "gender",
            "hair_color",
            "height",
            "homeworld",
            "mass",
            "name",
            "skin_color",
        )
        transformed_table = etl.records(transformed_table)
        assert transformed_table[0]["date"] == date(2014, 12, 20)
        assert transformed_table[0]["homeworld"] == self.planet_name


@pytest.mark.django_db
class TestCharactersDetailView():
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()
        file = 'test.csv'
        self.instance = CharactersCsvFile()
        self.instance.file.name = file
        self.instance.save()


    def test_404_when_no_instance(self):
        request = self.factory.get('/characters/1')
        CharactersCsvFile.objects.all().delete()
        with pytest.raises(Http404):
            CharactersDetailView.as_view()(request, pk=1)

    def test_404_when_no_file(self):
        request = self.factory.get(f'/characters/{self.instance.id}')
        with pytest.raises(Http404):
            CharactersDetailView.as_view()(request, pk=self.instance.id)

    @mock.patch('characters.tests.CharactersDetailView.get_records')
    def test_200(self, mocked):
        request = self.factory.get(f'/characters/{self.instance.id}')
        CharactersDetailView.as_view()(request, pk=self.instance.id)
