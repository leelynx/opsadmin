from django.conf.urls import url
from opstask.play import release
urlpatterns = [
    url(r'^config/update', release.play_release_config, name='play_release_config'),
    url(r'^config/compare', release.play_config_compare, name='play_config_compare'),
]