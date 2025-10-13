from django.conf import settings
from django.conf.urls.static import static  
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from rest_framework.authtoken import views 
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'), 
    path('admin/', admin.site.urls),

    # --- RUTAS DE LA API REST ---
    # 1. Endpoint para obtener el Token (POST username y password, devuelve el token)
    path('api/token-auth/', views.obtain_auth_token, name='api_token_auth'), 

    # 2. Ruta principal de la API v1 (Conecta a gestion_aerolinea/api_urls.py)
    path('api/v1/', include('gestion_aerolinea.api_urls')),

    # 3. Rutas de Documentación (Swagger UI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns += i18n_patterns(
    path('', include('home.urls')),
    path('', include('gestion_aerolinea.urls')),
)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )