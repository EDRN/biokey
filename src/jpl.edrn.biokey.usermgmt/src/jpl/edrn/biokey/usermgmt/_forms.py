# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: forms.'''

from .constants import GENERIC_FORM_TEMPLATE
from ._theme import bootstrap_form_widgets
from django import forms
from django.forms.utils import ErrorList
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class BootstrapErrorList(ErrorList):
    '''Custom ErrorList that uses a Bootstrap-compatible default CSS class.'''
    def __init__(self, initlist=None, error_class=None, renderer=None):
        if error_class is None:
            error_class = 'text-info'
        super().__init__(initlist, error_class, renderer)


class AbstractForm(forms.Form):
    '''This is an abstract form that sets up our preferred styles.'''
    template_name = 'jpl.edrn.biokey.usermgmt/form-rendering.html'
    template_name_label = 'jpl.edrn.biokey.usermgmt/label-rendering.html'
    error_css_class = 'is-invalid'
    required_css_class = 'is-required'

    def __init__(
        self,
        data=None,
        files=None,
        auto_id='id_%s',
        prefix=None,
        initial=None,
        error_class=BootstrapErrorList,
        label_suffix=None,
        empty_permitted=False,
        field_order=None,
        use_required_attribute=None,
        renderer=None,
        page=None
    ):
        super().__init__(
            data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
            use_required_attribute, renderer
        )
        self.page = page

    @staticmethod
    def get_encoding_type() -> str:
        '''Subclasses can override this if they need something other than ``application/x-www-form-urlencoded``.'''
        return 'application/x-www-form-urlencoded'

    class Meta:
        abstract = True


class AbstractFormPage(Page):
    '''Abstract base class for Wagtail pages holding Django forms.'''
    intro = RichTextField(blank=True, help_text='Introductory text to appear above the form')
    outro = RichTextField(blank=True, help_text='Text to appear below the form')
    preview_modes = []
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('outro')
    ]

    def get_form(self) -> type:
        '''Return the class of the form this page will display.'''
        raise NotImplementedError('Subclasses must implement get_form')

    # def get_encoding_type(self) -> str:
    #     cls = self.get_form()
    #     return cls.get_encoding_type()

    def get_initial_values(self, request: HttpRequest) -> dict:
        '''Return any initial values for the form. By default this is an empty dict.
        Subclasses may override this.'''
        return dict()

    def process_submission(self, form: forms.Form) -> dict:
        '''Process the submitted and cleaned ``form``.

        Return a dict of any other parameters that may be needed in the thank you page.
        '''
        raise NotImplementedError('Subclasses must implement process_submission')

    def get_landing_page(self) -> str:
        '''Get the name of the landing (thank you) page for successful submission.'''
        raise NotImplementedError('Subclasses must implement get_landing_page')

    def _bootstrap(self, form: forms.Form):
        '''Add Boostrap class to form widgets.'''
        bootstrap_form_widgets(form)

    def serve(self, request: HttpRequest) -> HttpResponse:
        form_class = self.get_form()
        if request.method == 'POST':
            form = form_class(request.POST, request.FILES, page=self)
            if form.is_valid():
                params = {'page': self, **self.process_submission(form)}
                return render(request, self.get_landing_page(), params)
        else:
            form = form_class(initial=self.get_initial_values(request), page=self)
        self._bootstrap(form)
        return render(request, GENERIC_FORM_TEMPLATE, {'page': self, 'form': form})

    class Meta:
        abstract = True
