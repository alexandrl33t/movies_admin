from django.urls import path

from movies.api.v1 import views

urlpatterns = [
    path('movies/', views.MoviesListApi.as_view(), name='movies-list'),
    path('movies/<uuid:pk>', views.MoviesDetailApi.as_view(), name='movies-detail'),
]
