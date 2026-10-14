from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import License, LicenseAccess, can_access


class CanAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', password='pw')
        self.license = License.objects.create(
            name='Adobe', key='XXXX', owner=self.owner
        )
        self.blocked = Group.objects.create(name='Contractors')
        self.allowed = Group.objects.create(name='Staff')
        self.user = User.objects.create_user('bob', password='pw')
        self.other = User.objects.create_user('ann', password='pw')

        self.user.groups.add(self.blocked)
        self.other.groups.add(self.allowed)
        LicenseAccess.objects.create(
            license=self.license, group=self.blocked, is_blocked=True
        )

    def test_blocked_group_is_denied(self):
        self.assertFalse(can_access(self.user, self.license))

    def test_other_group_stays_unlocked(self):
        self.assertTrue(can_access(self.other, self.license))

    def test_owner_bypasses_block(self):
        self.blocked.user_set.add(self.owner)
        self.assertTrue(can_access(self.owner, self.license))


class LicenseViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', password='pw')
        self.license = License.objects.create(
            name='Figma', key='SECRET', owner=self.owner
        )
        self.blocked = Group.objects.create(name='Interns')
        LicenseAccess.objects.create(
            license=self.license, group=self.blocked, is_blocked=True
        )
        self.member = User.objects.create_user('member', password='pw')
        self.member.groups.add(self.blocked)
        self.outsider = User.objects.create_user('outsider', password='pw')

    def test_blocked_member_forbidden_on_detail(self):
        self.client.force_login(self.member)
        response = self.client.get(
            reverse('vault:license_detail', args=[self.license.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_unblocked_user_can_view_detail(self):
        self.client.force_login(self.outsider)
        response = self.client.get(
            reverse('vault:license_detail', args=[self.license.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SECRET')

    def test_list_hides_blocked_license(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse('vault:license_list'))
        self.assertNotContains(response, 'Figma')

    def test_only_owner_can_manage_access(self):
        self.client.force_login(self.outsider)
        response = self.client.get(
            reverse('vault:license_access', args=[self.license.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_block_group(self):
        group = Group.objects.create(name='Vendors')
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('vault:license_access', args=[self.license.pk]),
            {'blocked_groups': [group.pk]},
        )
        self.assertRedirects(
            response, reverse('vault:license_detail', args=[self.license.pk])
        )
        self.assertTrue(
            LicenseAccess.objects.filter(
                license=self.license, group=group, is_blocked=True
            ).exists()
        )
