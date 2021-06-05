from django.conf.urls import url
from COVID import views
from django.conf.urls.static import static
from django.conf import settings

# 1.在应用中进行urls配置的时候;
# (1)严格匹配开头和结尾

urlpatterns = [

                  url(r'^base$', views.base),  # base

                  url(r'^$', views.index),  # index
                  url(r'^index$', views.index),
                  url(r'^distribution$', views.distribution),  # distribution
                  url(r'^route$', views.route),  # route
                  url(r'^add_points$', views.add_points),  # add risk point
                  url(r'^infected_points$', views.infected_points),  # add risk point
                  url(r'^reload$', views.reload),  # reload data

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
