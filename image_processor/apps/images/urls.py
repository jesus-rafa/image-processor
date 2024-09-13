from django.urls import path
from . import views
app_name = "images_app"

urlpatterns = [
    path(
        'api/images/v1/remove-background/<str:bucket>/<str:image_url>/',
        views.Remove_Background.as_view()
    ),
    path(
        'api/images/v1/extract-colors/<str:bucket>/<str:image_url>/',
        views.Extract_Colors.as_view()
    ),
]