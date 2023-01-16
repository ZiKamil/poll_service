from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('registration/', views.user_registration, name='registration'),
    path('logout/', views.user_logout, name='logout'),

    path('statistics/', views.StatisticsView.as_view(), name='statistics'),

    path('test/', views.TestListView.as_view(), name='test'),
    path('test/<int:pk>', views.TestPassView.as_view(), name='test-pass'),
    path('test/<int:test_id>/question/<int:question_id>', views.question_view, name='question'),

    path('marketplace/' , views.MarketplaceView.as_view(), name='marketplace'),
    path('marketplace/<int:pk>', views.frame_view, name='frame'),
    path('my_frames/', views.MyFramesView.as_view(), name='my-frames'),
    path('my_frames/<int:pk>', views.my_frame_view, name='my-frame')
]
