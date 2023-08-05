from appconf import AppConf

from django.conf import settings  # NOQA
from django.utils.translation import ugettext_lazy as _


class AoxomoxoaAppConf(AppConf):
    # default module name for this app cms plugins
    MODULE_NAME = 'Aoxomoxoa'

    # unite gallery skins
    UNITE_SKINS = (
        ('default', _('Default')),
        ('alexis', _('Alexis')),
    )

    # do I need to load jquery?
    NEEDS_JQUERY = True

    class Meta:
        prefix = 'ripiu_aoxomoxoa'
