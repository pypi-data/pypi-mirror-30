from django.conf.urls import url, include

urlpatterns = [
    url(r'^trumbowyg/', include('trumbowyg.urls'))
]