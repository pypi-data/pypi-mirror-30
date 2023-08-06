# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import CheckboxSelectMultiple


class TranslateCheckboxSelectMultipleWidget(CheckboxSelectMultiple):
    queryset = None

    def __init__(self, queryset, *args, **kwargs):
        super(TranslateCheckboxSelectMultipleWidget, self).__init__(*args, **kwargs)
        self.queryset = queryset

    class Media:
        js = [
            'http://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.js',
            'js/translate_checkbox_select_multiple.js'
        ]

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        optgroups = []
        
        for group, option, index in context['widget']['optgroups']:
            attrs = option[0]['attrs']
            obj = self.queryset.filter(pk=option[0]['value']).first()
            attrs['data-lang'] = obj.lang
            optgroups.append(
                (
                    group,
                    [
                        {
                            u'index': index,
                            u'name': option[0]['name'],
                            u'template_name': option[0]['template_name'],
                            u'type': option[0]['type'],
                            u'selected': option[0]['selected'],
                            u'attrs': attrs,
                            u'value': option[0]['value'],
                            u'label': option[0]['label']
                        }
                    ],
                    index
                )
            )
        return self._render(self.template_name, context, renderer)