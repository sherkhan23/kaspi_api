from django.contrib import admin

from admin_panel.telebot.models import Account, RequestLog, Transaction


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'level', 'endpoint', 'message')
    list_filter = ('level', 'endpoint', 'created_at')
    search_fields = ('message', 'details', 'endpoint')
    readonly_fields = ('level', 'endpoint', 'message', 'details', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'account', 'name', 'sum', 'email', 'kaspi_order_id')
    search_fields = ('phone', 'account', 'name', 'email', 'sb_id', 'kaspi_order_id')
    list_filter = ('payment_title',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('txn_id', 'account', 'sum', 'result', 'txn_date', 'comment')
    search_fields = ('txn_id', 'account', 'comment')
    list_filter = ('result', 'command')
