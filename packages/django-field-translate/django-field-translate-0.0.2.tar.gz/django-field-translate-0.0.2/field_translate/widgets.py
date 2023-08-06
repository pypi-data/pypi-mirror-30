# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ModelMultiChoiceWidget(forms.Widget):
    template_name = 'admin/checkbox_select_with_lang.html'
    queryset = None

    class Media:
        js = [
            'http://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.js',
            'js/model_multi_choice_widget.js'
        ]

    def __init__(self, queryset):
        super(ModelMultiChoiceWidget, self).__init__()
        self.queryset = queryset

    def get_options(self, context):
        options = []
        for obj in self.queryset:
            options.append(
                (
                    None,
                    [
                        {
                            u'index': len(options),
                            u'name': context['widget']['name'],
                            u'template_name': u'admin/checkbox_option.html',
                            u'type': u'checkbox',
                            u'selected': False,
                            u'attrs': {},
                            u'value': obj.pk,
                            u'label': obj.__unicode__,
                            u'lang': obj.lang,
                        }
                    ],
                    len(options)
                )
            )
        return options

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)

        context['widget']['optgroups'] = self.get_options(context)

        return mark_safe(
            render_to_string(
                self.template_name,
                context

            )
        )
