from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin, ImportMixin, ExportMixin
from import_export.forms import ImportForm, ConfirmImportForm, ExportForm
import tempfile
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.sites import AlreadyRegistered
#from django.db.models.loading import get_models, get_app
from emails.utils import TypeManager
from suit.widgets import SuitDateWidget, SuitTimeWidget, SuitSplitDateTimeWidget
from django import forms
from django.template import Context,Template
from import_export import resources
from django.contrib.auth.models import User

from common.admin import CustomExportMixin,CustomImportMixin,CustomImportExportMixin,CustomImportExportModelAdmin, AssignToContractUserAdmin


class IPAFileAdminInline(admin.TabularInline):
    model = IPAFile

class AppAdmin(CustomImportExportModelAdmin):
    list_display=['appName','contractUser','appID','appVersion','appType','appLink','appTabLink']
    inlines=[IPAFileAdminInline]

class UsuarioLDAPAdmin(CustomImportExportModelAdmin):
    list_filter=['usuario','macaddress']
    list_display=['usuario','macaddress']
    search_fields = ['usuario','macaddress']


class DeliveryQueueInline(admin.TabularInline):
    model = DeliveryQueue
    can_delete = False
    can_change = False
    readonly_fields = ('appinstance',)
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EnvioProgramadoForm(forms.ModelForm):

    class Meta:
        model = Delivery
        fields = ['fecha','appinstance','plantilla']
        widgets = {
            'fecha': SuitSplitDateTimeWidget,
        }


class EnvioProgramadoAdmin(CustomImportExportModelAdmin):
    list_display=['__unicode__','enviados','aceptados','rechazados','pendientes']
    inlines = [DeliveryQueueInline]
    can_delete = False
    can_change = True
    def has_change_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return False
    pass

class NoChangePermisionAdmin(CustomImportExportModelAdmin):
    can_delete = True
    can_change = False
    can_add = False
    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True

    pass


class BalanceLimitDeployAdmin(CustomImportExportModelAdmin):
    list_display=['contractUser','saldo','total_contrato','usado','licence']
    can_add = False
    def has_add_permission(self, request, obj=None):
        user = User.objects.get(username=request.user.username)
        self.can_add = True if user.is_superuser else False
        return True if user.is_superuser else False
    pass

class CustomAdmin(CustomImportExportModelAdmin):
    pass

admin.site.register(AppInstance,AppAdmin)
admin.site.register(UsuarioLDAP,UsuarioLDAPAdmin)
admin.site.register(BalanceLimitDeploy,BalanceLimitDeployAdmin)
admin.site.register(ContractAPI)
admin.site.register(Delivery,EnvioProgramadoAdmin)
admin.site.register(DeliveryQueue,NoChangePermisionAdmin)
admin.site.register(DeployBashTemplate,CustomAdmin)
