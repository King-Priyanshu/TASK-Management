from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('signup/', views.signupPage, name='signup_page'),
    path('signup/submit/', views.signup, name='signup'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('login/', views.loginPage, name='login'),
    path('login/submit/', views.login, name='login_submit'),
    path('home/', views.home, name='home'),
    path('add/', views.addTask, name='addTask'),
    path('edit/', views.editTask, name='editTask'),
    path('delete/', views.deleteTask, name='deleteTask'),
    path('toggleTaskCompletion/', views.toggleTaskCompletion, name='toggleTaskCompletion'),
    path('logout/', views.logout_view, name='logout'),
    path('get-task-data/', views.get_task_data, name='get_task_data'),
    path('table/', views.table_view, name='table'),
    path('discription_view/', views.discription_view, name='discription_view'),
    path('stat/', views.stat, name='stat'),




]
