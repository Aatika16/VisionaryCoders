from django.urls import path
from . import views
from .views import translate_text ,login_view,signup_create,history_view,logout,profile,index,detect_lang

urlpatterns = [
    path('translater/', views.home, name='home'),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
    path('signup/', signup_create, name='signup'),
    path('profile/', profile, name='profile'),
    path('history/', history_view, name='history'),
    path('translate/', translate_text, name='translate_text'),
    path('detectlang/', detect_lang, name='detect_lang'),
]
# main/urls.py

