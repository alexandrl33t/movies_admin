from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from math import ceil

from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return FilmWork.objects.annotate(
            genres_names=ArrayAgg('genres__name', distinct=True, default=[]),
            actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role='actor'), distinct=True, default=[]),
            writers=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role='writer'), distinct=True, default=[]),
            directors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role='director'), distinct=True, default=[]),
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False)

    def object_to_json(self, obj):
        return {
            'id': obj.id,
            'title': obj.title,
            'description': obj.description,
            'creation_date': obj.creation_date,
            'rating': obj.rating,
            'type': obj.type,
            'genres': obj.genres_names,
            'actors': obj.actors,
            'writers': obj.writers,
            'directors': obj.directors,
        }


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)

        total_pages = ceil(paginator.count / self.paginate_by)

        context = {
            'count': paginator.count,
            'total_pages': total_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': [self.object_to_json(item) for item in queryset],
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        if not (film := self.get_queryset().filter(id=self.kwargs['pk']).first()):
            return JsonResponse({"error": "Detail not found"}, status=404)
        return self.object_to_json(film)
