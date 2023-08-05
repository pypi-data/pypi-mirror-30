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


class EmailSubscriberResource(resources.ModelResource):

    class Meta:
        model = EmailSubscriber
        import_id_fields = ('email','contractUser')

class EmailSubscriberAdmin(CustomImportExportModelAdmin):
    list_display=['email','rut','nombre','apellido','apellido2','contractUser']
    resource_class = EmailSubscriberResource
    change_list_template = 'admin/qsms/change_list_import_export_addbasedatos.html'
    pass


class EmailSubscriberBaseDatosInline(admin.TabularInline):
    model = EmailBaseDatos
    can_delete = False
    can_change = False
    readonly_fields = ('email',)
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class DeliveryQueueInline(admin.TabularInline):
    model = DeliveryQueue
    can_delete = False
    can_change = False
    readonly_fields = ('email',)
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class BaseDatosAdmin(CustomImportExportModelAdmin):
    inlines = [EmailSubscriberBaseDatosInline]
    change_list_template = 'admin/qsms/change_list_import_export_addplantilla.html'

class PlantillaAdmin(CustomImportExportModelAdmin):
    change_list_template = 'admin/qsms/change_list_import_export_addenvioprogramado.html'

class EnvioProgramadoForm(forms.ModelForm):

    class Meta:
        model = Delivery
        fields = ['fecha','basedatos','plantilla']
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
class SaldoEmailsAdmin(CustomImportExportModelAdmin):
    list_display=['contractUser','saldo','total_contrato','usado','licence']
    can_add = False
    def has_add_permission(self, request, obj=None):
        user = User.objects.get(username=request.user.username)
        self.can_add = True if user.is_superuser else False
        return True if user.is_superuser else False
    pass

class CustomAdmin(CustomImportExportModelAdmin):
    pass

admin.site.register(EmailSubscriber,EmailSubscriberAdmin)
admin.site.register(BaseDatos,BaseDatosAdmin)

admin.site.register(EmailBaseDatos,NoChangePermisionAdmin)
admin.site.register(Delivery,EnvioProgramadoAdmin)
admin.site.register(DeliveryQueue,NoChangePermisionAdmin)
admin.site.register(EmailTemplate,PlantillaAdmin)
admin.site.register(ContractEmail)
admin.site.register(SaldoEmails,SaldoEmailsAdmin)
