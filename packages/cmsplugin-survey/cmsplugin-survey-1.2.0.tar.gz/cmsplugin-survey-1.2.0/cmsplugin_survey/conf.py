from __future__ import unicode_literals

from appconf import AppConf
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class CmspluginSurveyAppConf(AppConf):

    TEMPLATES = [
        ('default', _('default')),
    ]

    class Meta:
        prefix = 'CMSPLUGIN_SURVEY'

