from django.views.generic import ListView, DetailView
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
import petl as etl

from characters.models import CharactersCsvFile
from characters.importer import CharacterImporter

DEFAULT_ROWS_LIMIT = 10


class CharactersListView(ListView):
    paginate_by = 10
    model = CharactersCsvFile


class CharactersDetailView(DetailView):
    model = CharactersCsvFile

    def get_records(self, count_columns: str, limit: int, model: CharactersCsvFile) -> dict:
        dataset = etl.fromcsv(settings.MEDIA_ROOT / model.file.name)
        headers = etl.header(dataset)
        if count_columns:
            columns = count_columns.split(",")[:-1]
            aggregated_dataset = etl.aggregate(
                dataset[: limit + 1], key=columns, aggregation=len
            )
            aggregated_headers = etl.header(aggregated_dataset)
            aggregated_records = etl.records(aggregated_dataset)
        else:
            aggregated_headers = aggregated_records = None
        records = etl.records(dataset)[:limit]
        return {
            "headers": headers,
            "records": records,
            "limit": limit,
            "count_columns": count_columns,
            "aggregated_headers": aggregated_headers,
            "aggregated_records": aggregated_records,
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        parameters = self.request.GET
        limit = int(parameters.get("limit", DEFAULT_ROWS_LIMIT))
        count_columns = parameters.get("count_columns", "")
        try:
            context_records = self.get_records(count_columns, limit, context["object"])
        except FileNotFoundError:
            raise Http404()
        return context | context_records


def download_characters(request: HttpRequest) -> HttpResponseRedirect:
    importer = CharacterImporter()
    if imported_file := importer.import_data():
        messages.success(request, f"Added new file with id {imported_file.id} .")
    else:
        messages.error(request, "Unable to fetch new data at this point")
    return redirect("characters:characters-list")
