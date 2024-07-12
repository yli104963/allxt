# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create_document/', views.create_document, name='create_document'),
    path('document_list/', views.document_list, name='document_list'),
    path('document/<int:document_id>/', views.document_detail, name='document_detail'),
    path('document/<int:document_id>/process/', views.process_document, name='process_document'),
    path('transit_document/<int:document_id>/', views.transit_document, name='transit_document'),
    path('search/', views.search_documents, name='search_documents'),
    path('update/', views.update_delivery_time, name='update_delivery_time'),
    path('', views.index, name='index'),
]
