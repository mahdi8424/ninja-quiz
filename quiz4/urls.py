from django.contrib import admin
from django.urls import include, path
from home import views as home_views
from django.conf import settings
from django.conf.urls.static import static
from home.api import router as home_router
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI(version="1.0")
api.register_controllers(NinjaJWTDefaultController)
api.add_router("/home/", home_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("api/v1/", api.urls),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
