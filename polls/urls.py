from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('detail/<int:poll_id>/', views.detail, name='poll_detail'),
    path('create/', views.create, name='create_poll'),
    path('<int:poll_id>/create-comments/', views.create_comments, name='create_comments'),
    path('login/', views.my_login, name='login'),
    path('logout/', views.my_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('register/', views.register, name='register'),
    path('update/<int:poll_id>/', views.update, name='update_poll'),
    path('delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('<int:question_id>/add-choice/', views.add_choice, name='add_choice'),
    path('api/<int:question_id>/add-choice/', views.add_choice_api, name='add_choice_api'),
    path('api/<int:question_id>/get-choice/', views.get_choice_api, name='get_choice_api'),
    path('api/<int:choice_id>/delete-choice/', views.delete_choice_api, name='delete_choice_api'),
]
