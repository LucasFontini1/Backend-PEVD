from django.contrib import admin

from support.models import CommercialAudit, ContactInquiry, CustomQuote, FAQ, SupportMessage, SupportTicket


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'published', 'sort_order']
    list_filter = ['published']
    search_fields = ['question', 'answer']


class ReadOnlyRecordsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ContactInquiry, ReadOnlyRecordsAdmin)
admin.site.register(SupportTicket, ReadOnlyRecordsAdmin)
admin.site.register(SupportMessage, ReadOnlyRecordsAdmin)
admin.site.register(CustomQuote, ReadOnlyRecordsAdmin)
admin.site.register(CommercialAudit, ReadOnlyRecordsAdmin)
