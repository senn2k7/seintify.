from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('prediksi/', views.prediksi_nilai, name='prediksi'),
    path('ai/jelaskan/', views.ai_jelaskan, name='ai_jelaskan'),
]
