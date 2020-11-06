from django.conf.urls import include, url
from .views import home, part1, part2and3
urlpatterns = [  
    url(r'^(?P<filename>.*)/part1/$',part1),
    url(r'^(?P<filename>.*)/part2and3/$',part2and3),
    url('',home,name='home'),
]
