# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
import uuid

class PermabotsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)   
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True) 
    
    class Meta:
        abstract = True