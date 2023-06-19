
from django.urls import path

from note import views

urlpatterns = [
    path('all', views.list_view),
    path('add', views.add_view),
    path('update_note/<int:note_id>', views.update_view),
    path('delete_note', views.delete_view)

]