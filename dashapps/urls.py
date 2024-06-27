from django.urls import path,include 
from .views import HomeView


urlpatterns = [
path('', HomeView.as_view(), name='home'),
path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
