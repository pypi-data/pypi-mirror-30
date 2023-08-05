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

class CustomExportMixin(ExportMixin):
    def export_action(self, request, *args, **kwargs):
        formats = self.get_export_formats()
        form = ExportForm(formats, request.POST or None)
        if form.is_valid():
            file_format = formats[
                int(form.cleaned_data['file_format'])
            ]()

            resource_class = self.get_resource_class()
            queryset = self.get_export_queryset(request)
            data = resource_class().export(queryset)
            response = HttpResponse(
                file_format.export_data(data),
                mimetype='application/octet-stream',
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % (
                self.get_export_filename(file_format),
            )
            return response

        context = {}
        context['form'] = form
        context['opts'] = self.model._meta
        return TemplateResponse(request, [self.export_template_name],
                                context,
                                #current_app=self.admin_site.name
                                )

class CustomImportMixin(ImportMixin):
    def process_import(self, request, *args, **kwargs):
        '''
        Perform the actuall import action (after the user has confirmed he
        wishes to import)
        '''
        opts = self.model._meta
        resource = self.get_resource_class()()

        confirm_form = ConfirmImportForm(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            import_file = open(request.POST['import_file_name'],
                               input_format.get_read_mode())
            data = import_file.read()
            if confirm_form.cleaned_data['input_format']=='0': #CSV
                data = data.replace(';',',')
                data = data.replace('(u)','')
                data = data.replace('($)','')
                data = data.replace('"','')
            if not input_format.is_binary() and self.from_encoding:
                try:
                    data = unicode(data, self.from_encoding).encode('utf-8')
                except:
                    typeManager = TypeManager()
                    data = typeManager.force_unicode(data, strings_only=True).encode('utf-8')
            dataset = input_format.create_dataset(data)
            if hasattr(self,'custom_headers_xls'):
                dataset.headers = self.custom_headers_xls
            else:
                dataset.headers = [d.replace('(u)','').replace('($)','') for d in dataset.headers  ]

            resource.import_data(dataset, dry_run=False,
                                 raise_errors=False)


            success_message = _('Import finished')
            messages.success(request, success_message)
            import_file.close()

            url = reverse('admin:%s_%s_changelist' %
                          (opts.app_label, opts.model_name),
#                          current_app=self.admin_site.name
                          )
            return HttpResponseRedirect(url)


    def import_action(self, request, *args, **kwargs):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = self.get_resource_class()()

        context = {}

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          request.POST or None,
                          request.FILES or None)

        if request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if form.cleaned_data['input_format']=='0': #CSV
                    data = data.replace(';',',')
                    data = data.replace('(u)','')
                    data = data.replace('($)','')
                    data = data.replace('"','')
                if not input_format.is_binary() and self.from_encoding:
                    try:
                        data = unicode(data, self.from_encoding).encode('utf-8')
                    except:
                        typeManager = TypeManager()
                        data = typeManager.force_unicode(data, strings_only=True).encode('utf-8')
#                try:
                dataset = input_format.create_dataset(data)
#                except Exception, ex:
#                    print str(ex)
#                    pass

#                print [resource.fields[f] for f in resource.get_export_order()]
#                print resource.fields
#                print resource.get_export_order()

#                print dataset.headers
                if hasattr(self,'custom_headers_xls'):
                    dataset.headers = self.custom_headers_xls
                else:
                    dataset.headers = [d.replace('(u)','').replace('($)','') for d in dataset.headers  ]
#                print dataset.headers

#                result = resource.import_data(dataset, dry_run=True,
#                                              raise_errors=False)
                result = resource.import_data(dataset, dry_run=False,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': uploaded_file.name,
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(request, [self.import_template_name],
                                context,
#                                current_app=self.admin_site.name
                                )

class CustomImportExportMixin(CustomImportMixin, CustomExportMixin):
    """
    Import and export mixin.
    """
    #: template for change_list view
    change_list_template = 'admin/import_export/change_list_import_export.html'


class CustomImportExportModelAdmin(CustomImportExportMixin, admin.ModelAdmin):
    """
    Subclass of ModelAdmin with import/export functionality.
    """



class EmailAdmin(CustomImportExportModelAdmin):
    list_display=['rut','email','nombre','apellido','apellido2']
    pass

class LinkCounterAdmin(CustomImportExportModelAdmin):
    list_display=['plantilla','link','clicks']
    pass

class EmailBaseDatosInline(admin.TabularInline):
    model = EmailBaseDatos

class BaseDatosAdmin(CustomImportExportModelAdmin):
    inlines = [EmailBaseDatosInline]

class EnvioProgramadoForm(forms.ModelForm):

    class Meta:
        model = Delivery
        fields = ['fecha','basedatos','plantilla']
        widgets = {
            'fecha': SuitSplitDateTimeWidget,
        }


class EnvioProgramadoAdmin(CustomImportExportModelAdmin):
#    form = EnvioProgramadoForm
    pass

admin.site.register(Email,EmailAdmin)
admin.site.register(LinkCounter,LinkCounterAdmin)
admin.site.register(BaseDatos,BaseDatosAdmin)

admin.site.register(EmailBaseDatos,CustomImportExportModelAdmin)
admin.site.register(Delivery,EnvioProgramadoAdmin)
admin.site.register(DeliveryQueue,CustomImportExportModelAdmin)
admin.site.register(EmailTemplate,CustomImportExportModelAdmin)

"""
def autoregister(*app_list):

    for app_name in app_list:
        app_models = get_app(app_name)
        for model in get_models(app_models):
            try:
                admin.site.register(model,CustomImportExportModelAdmin)
            except AlreadyRegistered:
                pass

autoregister('emails')
"""
