from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', views.home, name='home'),

#    path('login/', views.login_view, name='login'),
#    path('logout/', views.logout_view, name='logout'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()