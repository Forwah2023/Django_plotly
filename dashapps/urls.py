from django.urls import path,include 
from .views import HomeView,AboutView


urlpatterns = [
path('', HomeView.as_view(), name='home'),
path('about', AboutView.as_view(), name='about'),
path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
