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

class CustomExportMixin(ExportMixin):
    pass

class AssignToContractUserAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(AssignToContractUserAdmin, self).get_queryset(request)
        user = Contract.objects.get(username=request.user.username)
        if user.is_superuser:
            return qs
        return qs.filter(contractUser=user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'contractUser':
            kwargs['queryset'] = Contract.objects.filter(username=request.user.username)
#            kwargs['queryset'] = Contract.objects.all()
        return super(AssignToContractUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        if obj is not None:
            user = Contract.objects.get(username=request.user.username)
            return self.readonly_fields + ('contractUser',) if not user.is_superuser else self.readonly_fields
        """
        user = Contract.objects.get(username=request.user.username)
        return ('contractUser',)+ self.readonly_fields  if not user.is_superuser else self.readonly_fields

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'contractUser', None) is None:
            obj.contractUser = Contract.objects.get(username=request.user.username)
        obj.save()

    def add_view(self, request, form_url="", extra_context=None):
        data = request.GET.copy()
        data['contractUser'] = Contract.objects.get(username=request.user.username)
        request.GET = data
        return super(AssignToContractUserAdmin, self).add_view(request, form_url="", extra_context=extra_context)

    def get_foreign_keys(self):
        foreignkeys = []
        for f in self.model._meta.fields:
            if f.__repr__().split(':')[0].__contains__('ForeignKey'):
                foreignkeys.append(f)
        return foreignkeys

    def get_form(self, request, obj=None, **kwargs):
        form = super(AssignToContractUserAdmin, self).get_form(request, obj, **kwargs)
        user = Contract.objects.get(username=request.user.username)
        for foreignkey in self.get_foreign_keys():
            if (not user.is_superuser) and (foreignkey.name is not 'contractUser'):
                form.base_fields[foreignkey.name].queryset = form.base_fields[foreignkey.name].queryset.filter(contractUser__username=request.user.username)
        return form

    def get_changelist(self, request, **kwargs):
        from django.contrib.admin.views.main import ChangeList
        from django.db.models import Q

        # Define a custom ChangeList class with a custom queryset
        class ActiveChangeList(ChangeList):
            def get_query_set(self, *args, **kwargs):
                user = Contract.objects.get(username=request.user.username)
                qs = super(ActiveChangeList, self).get_query_set(*args, **kwargs)
                if (not user.is_superuser):
                    qs = qs.filter(Q(contractUser=user))
                return qs
            def queryset(self, *args, **kwargs):
                user = Contract.objects.get(username=request.user.username)
                qs = super(ActiveChangeList, self).get_query_set(*args, **kwargs)
                if (not user.is_superuser):
                    qs = qs.filter(Q(contractUser=user))
                return qs

        # use the custom ChangeList class if the parameter exists
        return ActiveChangeList


class CustomImportMixin(ImportMixin):
    """
    Import and export mixin.
    """

class CustomImportExportMixin(CustomImportMixin, CustomExportMixin):
    """
    Import and export mixin.
    """
    #: template for change_list view
    change_list_template = 'admin/import_export/change_list_import_export.html'


class CustomImportExportModelAdmin(CustomImportExportMixin, AssignToContractUserAdmin):
    """
    Subclass of ModelAdmin with import/export functionality.
    """

class CustomAdmin(CustomImportExportModelAdmin):
    pass

admin.site.register(Contract)
admin.site.register(API_BACKEND)
