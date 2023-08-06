=====
Location Maps
=====

Location é um projeto para simplificar todas as implementações de mapas no admin do django

Quick start
-----------

1. Add "location" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'field_translate',
    ]

2. Example usage::

    # models.py
    from django.conf import settings

    class ExampleRelationModel(models.Model):
        lang = models.CharField(max_length=10, blank=False, choices=settings.LANGUAGES)
        title = models.CharField(max_length=255, )


    class ExampleModel(models.Model):
        lang = models.CharField(_('Idioma'), max_length=10, blank=False, choices=settings.LANGUAGES)
        title = models.CharField(max_length=255, )
        field_relation = models.ManyToManyField(ExampleRelationModel, blank=False)


    # forms.py
    from field_translate.widgets import ModelMultiChoiceWidget

    class ExampleAdminForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(ExampleAdminForm, self).__init__(*args, **kwargs)
            self.fields['field_relation'].widget = ModelMultiChoiceWidget(queryset=ExampleRelationModel.objects.all())


    # admin.py
    class ExampleAdmin(admin.ModelAdmin):
        form = ExampleAdminForm

        def get_changeform_initial_data(self, request):
            return {'lang': request.user.lang}

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to visit the example form (you'll need the Admin app enabled).