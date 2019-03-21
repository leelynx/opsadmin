from django.conf.urls import url
from opstask.pcloud import release, rollback
urlpatterns = [
    url(r'^release', release.pcloud_release_code, name='pcloud_release_code'),
    url(r'^code/update', release.pcloud_increment_release_code, name='pcloud_increment_release_code'),
    url(r'^config/update', release.pcloud_release_config, name='pcloud_release_config'),
    url(r'^app/list',release.pcloud_get_app_list, name="pcloud_get_app_list"),
    url(r'^get/group', release.pcloud_get_ansible_group, name='pcloud_get_ansible_group'),
    url(r'^restart', release.pcloud_restart_process, name='pcloud_restart_process'),
    url(r'^appcode/rollback', rollback.pcloud_rollback_code, name='pcloud_rollback_code'),
    url(r'^appconf/rollback', rollback.pcloud_rollback_config, name='pcloud_rollback_config'),
    url(r'^get/backup', rollback.pcloud_get_backup_file, name='pcloud_get_backup_file'),
]
