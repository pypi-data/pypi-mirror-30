# -*- coding: utf-8 -*-

import shortuuid
from django.conf import settings


class _CurtailUUID:
    def __init__(self):
        self.length = hasattr(settings, 'CURTAIL_UUID_LENGTH') and settings.CURTAIL_UUID_LENGTH or 22

    def uuid(self, model, field='uuid', length=None, upper=False):
        flag = True
        while flag:
            uuid = shortuuid.ShortUUID().random(length=length or self.length)
            if upper:
                uuid = uuid.upper()
            try:
                model.objects.get(**{field: uuid})
            except model.DoesNotExist:
                flag = False
        return uuid


CurtailUUID = _CurtailUUID()
uuid = CurtailUUID.uuid
