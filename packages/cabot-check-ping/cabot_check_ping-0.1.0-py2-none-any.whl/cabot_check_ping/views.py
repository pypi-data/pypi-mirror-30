from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from cabot.cabotapp.models import StatusCheck
from cabot.cabotapp.views import (CheckCreateView, CheckUpdateView,
                                  StatusCheckForm, base_widgets)

from .models import PingStatusCheck


class PingStatusCheckForm(StatusCheckForm):
    symmetrical_fields = ('service_set', 'instance_set')

    class Meta:
        model = PingStatusCheck
        fields = (
            'name',
            'host',
            'timeout',
            'packet_size',
            'count',
            'max_rtt',
            'frequency',
            'active',
            'importance',
            'debounce',
        )

        widgets = dict(**base_widgets)
        widgets.update({
            'host': forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': 'service.arachnys.com',
            })
        })


class PingCheckCreateView(CheckCreateView):
    model = PingStatusCheck
    form_class = PingStatusCheckForm


class PingCheckUpdateView(CheckUpdateView):
    model = PingStatusCheck
    form_class = PingStatusCheckForm


def duplicate_check(request, pk):
    pc = StatusCheck.objects.get(pk=pk)
    npk = pc.duplicate()
    return HttpResponseRedirect(reverse('update-ping-check', kwargs={'pk': npk}))
