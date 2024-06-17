# encoding: utf-8

'''🧬🔑🦦 BioKey content: models.'''

from jpl.edrn.biokey.streams import blocks
from wagtail import blocks as wagtail_core_blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index


class HomePage(Page):
    '''A page specifically for the home page of the site.'''

    template = 'jpl.edrn.biokey.content/home-page.html'
    page_description = 'A web page specifically for the home of the site'
    max_count = 1

    body = StreamField([
        ('title', blocks.TitleBlock()),
        ('rich_text', wagtail_core_blocks.RichTextBlock(
            label='Rich Text',
            icon='doc-full',
            help_text='Richly formatted text',
        )),
        ('block_quote', blocks.BlockQuoteBlock(help_text='Block quote')),
        ('raw_html', wagtail_core_blocks.RawHTMLBlock(help_text='Raw HTML (use with care)')),
    ], null=True, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]

    class Meta:
        verbose_name = 'home page'
        verbose_name_plural = 'home pages'


class FlexPage(Page):
    '''A flexible page that has a stream of various fields.'''

    template = 'jpl.edrn.biokey.content/flex-page.html'
    page_description = 'Generic web page with a sequence of block content'

    body = StreamField([
        ('title', blocks.TitleBlock()),
        ('rich_text', wagtail_core_blocks.RichTextBlock(
            label='Rich Text',
            icon='doc-full',
            help_text='Richly formatted text',
        )),
        ('block_quote', blocks.BlockQuoteBlock(help_text='Block quote')),
        ('raw_html', wagtail_core_blocks.RawHTMLBlock(help_text='Raw HTML (use with care)')),
    ], null=True, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.AutocompleteField('body'),
    ]

    class Meta:
        verbose_name = 'web page'
        verbose_name_plural = 'web pages'
