# encoding: utf-8

'''🧬🔑🦦 BioKey streams: blocks.'''

from django.forms.utils import ErrorList
from django.utils.html import format_html
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.contrib.table_block.blocks import TableBlock as BaseTableBlock
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock as BaseTypedTableBlock
from wagtail.images.blocks import ImageChooserBlock


class TitleBlock(blocks.StructBlock):
    '''A large title.'''
    text = blocks.CharBlock(max_length=100, required=True, help_text='Title to display')
    class Meta:
        template = 'jpl.edrn.biokey.streams/title-block.html'
        icon = 'title'
        label = 'Title'
        help_text = 'Large title text to display on the page'


class BlockQuoteBlock(blocks.BlockQuoteBlock):
    '''Override Wagtail's own BlockQuoteBlock so we can use Bootstrap styling.'''
    def render_basic(self, value, context=None):
        if value:
            return format_html('<blockquote class="blockquote"><p>{0}</p></blockquote>', value)
        else:
            return ''
