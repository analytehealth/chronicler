''' Audit Log Models '''
import json

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django import dispatch

from .utils import serialize_data, data_has_changes

audit = dispatch.Signal(
        providing_args=['instance', 'relations', 'user', 'force'])


class AuditItem(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    serialized_data = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User', null=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def audit_data(self):
        return json.loads(self.serialized_data)

    class Meta:
        ordering = ('-created',)
        get_latest_by = 'created'


@dispatch.receiver(audit, weak=False, dispatch_uid='audit.create_audit')
def create_audit(sender, instance, relations, user, force=False, **kws):
    data = serialize_data(instance, relations)
    ct = ContentType.objects.get_for_model(instance)
    try:
        prev_audit = AuditItem.objects.filter(content_type=ct).latest()
    except AuditItem.DoesNotExist:
        prev_audit = None
    if data_has_changes(instance, relations, prev_audit) or force:
        AuditItem.objects.create(
            content_object=instance,
            user=user,
            serialized_data=json.dumps(data)
        )
