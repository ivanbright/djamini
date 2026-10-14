from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse


class License(models.Model):
    name = models.CharField(max_length=200)
    vendor = models.CharField(max_length=200, blank=True)
    key = models.CharField(max_length=500)
    notes = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='licenses',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vault:license_detail', args=[self.pk])

    @property
    def blocked_groups(self):
        return Group.objects.filter(
            license_rules__license=self, license_rules__is_blocked=True
        )

    def is_visible_to(self, user):
        return can_access(user, self)


class LicenseAccess(models.Model):
    # blocked group = no access. no row for a group = access stays open.
    license = models.ForeignKey(
        License, on_delete=models.CASCADE, related_name='access_rules'
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='license_rules'
    )
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('license', 'group')

    def __str__(self):
        state = 'blocked' if self.is_blocked else 'allowed'
        return f'{self.group} on {self.license}: {state}'


def can_access(user, license):
    # owner and superuser always get in; a blocked group does not
    if not user.is_authenticated:
        return False
    if user.is_superuser or license.owner_id == user.id:
        return True
    return not LicenseAccess.objects.filter(
        license=license,
        group__in=user.groups.all(),
        is_blocked=True,
    ).exists()
