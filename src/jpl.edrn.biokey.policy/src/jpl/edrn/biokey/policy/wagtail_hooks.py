# encoding: utf-8

'''🧬🔑 BioKey hooks into Wagtail.'''


from wagtail import hooks
from django.http import HttpRequest


@hooks.register('construct_page_action_menu')
def make_publish_default_action(menu_items: list, request: HttpRequest, context: dict):
    '''Instead of "Submit", make "Publish" the default on the save menu.'''
    for (index, item) in enumerate(menu_items):
        if item.name == 'action-publish':
            menu_items.pop(index)
            menu_items.insert(0, item)
            break
