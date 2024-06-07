'''🧬🔑🕴️ BioKey user management: theme and style.'''

from django import forms


def bootstrap_form_widgets(form: forms.Form):
    '''Add Boostrap class to every widget except checkboxes & radio buttons.'''
    for field in form.fields.values():
        if not isinstance(
            field.widget, (
                forms.widgets.CheckboxInput, forms.widgets.CheckboxSelectMultiple, forms.widgets.RadioSelect
            )
        ):
            field.widget.attrs.update({'class': 'form-control'})
