from django.contrib import admin

from .models import License, LicenseAccess


class LicenseAccessInline(admin.TabularInline):
    model = LicenseAccess
    extra = 0


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name', 'vendor')
    inlines = (LicenseAccessInline,)


@admin.register(LicenseAccess)
class LicenseAccessAdmin(admin.ModelAdmin):
    list_display = ('license', 'group', 'is_blocked')
    list_filter = ('is_blocked', 'group')
