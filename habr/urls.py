from django.contrib import admin
from django.urls import path, include
from articles import views as article_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', article_views.feed_all, name='home'),
    path('users/', include('users.urls')),
    path('articles/', include('articles.urls'))

]
