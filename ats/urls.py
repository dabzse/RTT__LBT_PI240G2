from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path("ajax/login/", views.ajax_login, name="xlogin"),
#    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path("jobs/", views.jobs_list, name="jobs-list"),
    path("jobs/<int:job_id>/", views.job_detail, name="job-detail"),
    path("jobs/detail/", views.job_detail, name="job-detail-empty"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
