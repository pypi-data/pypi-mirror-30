# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseModelMixin(models.Model):
    status = models.BooleanField(_(u'status'), default=True, help_text=_(u'Status'), db_index=True)
    created_at = models.DateTimeField(_(u'created_at'), auto_now_add=True, editable=True, help_text=_(u'Create Time'))
    updated_at = models.DateTimeField(_(u'updated_at'), auto_now=True, editable=True, help_text=_(u'Update Time'))

    class Meta:
        abstract = True


class SexModelMixin(models.Model):
    MALE = 1
    FEMALE = 0

    SEX_TUPLE = (
        (MALE, u'男'),
        (FEMALE, u'女'),
    )

    sex = models.BooleanField(_(u'sex'), choices=SEX_TUPLE, default=MALE, help_text=_(u'Sex'), db_index=True)

    class Meta:
        abstract = True
