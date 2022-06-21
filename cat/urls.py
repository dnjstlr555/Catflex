from django.urls import path
from . import views

app_name = 'cat'
urlpatterns = [


    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),



    path('genre/<str:genre_name>/', views.genrepage, name='genre'),
    #path('', views.Home, name='홈'),
    path('<int:movieid>/', views.MovieDetail, name='영화상세'),
    #path('LnD', views.LnD_Page, name='영화호불호'),

]

