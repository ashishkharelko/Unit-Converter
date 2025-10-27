from django import forms
from .models import UnitType, Unit

class ConversionForm(forms.Form):
    value = forms.FloatField(label='Value to convert')
    unit_type = forms.ModelChoiceField(queryset=UnitType.objects.all(), label='Unit Type')
    from_unit = forms.ModelChoiceField(queryset=Unit.objects.none(), label='From Unit')
    to_unit = forms.ModelChoiceField(queryset=Unit.objects.none(), label='To Unit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'unit_type' in self.data:
            try:
                unit_type_id = int(self.data.get('unit_type'))
                units = Unit.objects.filter(unit_type_id=unit_type_id)
                self.fields['from_unit'].queryset = units
                self.fields['to_unit'].queryset = units
            except (ValueError, TypeError):
                self.fields['from_unit'].queryset = Unit.objects.none()
                self.fields['to_unit'].queryset = Unit.objects.none()
        elif self.initial.get('unit_type'):
            unit_type_id = self.initial.get('unit_type')
            units = Unit.objects.filter(unit_type_id=unit_type_id)
            self.fields['from_unit'].queryset = units
            self.fields['to_unit'].queryset = units