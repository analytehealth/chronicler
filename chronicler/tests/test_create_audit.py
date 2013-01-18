''' Tests for chronicler.models.create_audit '''
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from chronicler.models import AuditItem, create_audit
from chronicler.tests import TestCase
from chronicler.tests.models import Person, Group, Membership


class TestCreateAudit(TestCase):

    def test_create_audit(self):
        ''' Tests audit.models.create_audit receiver. Asserts that we properly
        create an AuditItem
        '''
        person = Person.objects.create(name='Tester')
        user = User.objects.create(username='analyte')
        content_type = ContentType.objects.get_for_model(Person)
        group = Group.objects.create(name='group_one')
        group_two = Group.objects.create(name='group_two')
        member_one = Membership.objects.create(
            person=person,
            group=group,
            gold_member=True
        )
        member_two = Membership.objects.create(
            person=person,
            group=group_two,
            gold_member=False
        )

        create_audit(
            Person,
            person,
            ['membership_set'],
            user
        )
        audit = AuditItem.objects.get(
            content_type=content_type,
            object_id=person.pk
        )
        data = audit.audit_data
        audit_member_one, audit_member_two = data['membership_set']
        self.assertEqual(audit_member_one['id'], member_one.pk)
        self.assertEqual(audit_member_two['id'], member_two.pk)
        self.assertEqual(audit_member_one['group'], member_one.group.pk)
        self.assertEqual(audit_member_two['group'], member_two.group.pk)
        self.assertEqual(audit_member_one['gold_member'], True)
        self.assertEqual(audit_member_two['gold_member'], False)

        member_two.gold_member = True
        member_two.save()
        create_audit(
            Person,
            person,
            ['membership_set'],
            user
        )
        audit = AuditItem.objects.latest()
        self.assertEqual(
            audit.audit_data['membership_set'][1]['gold_member'],
            True
        )
