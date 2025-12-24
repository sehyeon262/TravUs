from django.urls import path
from .views import analyze_image, chat_ai, transcribe_audio, generate_spot_description

urlpatterns = [
    path('image/', analyze_image),
    path('chat/', chat_ai),
    path('speech/', transcribe_audio),
    path('spot-description/', generate_spot_description),
]
