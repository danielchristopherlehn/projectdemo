from django.contrib import admin
from .models import Liability

# This is the basic way to register it:
# admin.site.register(Liability)

# BUT, this is the PRO way so your admin panel looks super clean:


@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ('liability_name', 'liability_type',
                    'principal_amount', 'user', 'linked_asset')
    list_filter = ('liability_type', 'user')
    search_fields = ('liability_name',)
