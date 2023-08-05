from django.apps import AppConfig as BaseConfig
from django.utils.translation import ugettext_lazy as _


class SnapshotFieldConfig(BaseConfig):
    name = 'snapshot_field'
    verbose_name = _('Snapshot Field')
