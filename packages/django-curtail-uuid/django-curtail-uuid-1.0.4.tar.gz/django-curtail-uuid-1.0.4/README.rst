===================
django-curtail-uuid
===================

Installation
============

::

    pip install django-curtail-uuid


Usage
=====

::

    from account.models import LensmanInfo

    from django_curtail_uuid import CurtailUUID

    CurtailUUID.uuid(LensmanInfo, field='lensman_id', length=7)


Function
========

::

    CurtailUUID.uuid(model, field='uuid', length=None)


Settings.py
===========

::

    CURTAIL_UUID_LENGTH = 7

