# encoding: utf-8

'''🧬🔑 BioKey: site bloomer.'''


from django.conf import settings
from django.core.management.base import BaseCommand
from robots.models import Rule, DisallowedUrl
from wagtail.models import Site
from jpl.edrn.biokey.content.models import HomePage
from wagtail.rich_text import RichText
import argparse


class Command(BaseCommand):
    help = 'Blooms BioKey with initial content'
    _hostname = 'edrn-labcas.jpl.nasa.gov'
    _description = 'User profile management for cancer biomarker applications'
    _seo_title = 'EDRN BioKey User Profile Management'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--hostname', help='Hostname of the site (default: %(default)s)', default=self._hostname)

    def set_site(self, hostname: str):
        '''Set up the Wagtail `Site` object for BioKey.'''

        site = Site.objects.filter(is_default_site=True).first()
        site.site_name = 'BioKey'
        site.hostname = hostname 
        site.save()
        old_root = site.root_page.specific
        if old_root.title == 'BioKey':
            return site, old_root

        mega_root = old_root.get_parent()
        home_page = HomePage(
            title='BioKey', draft_title='🧬🔑 BioKey', seo_title=self._seo_title,
            search_description=self._description.strip(), live=True, slug=old_root.slug, path=old_root.path,
            depth=old_root.depth, url_path=old_root.url_path,
        )
        home_page.body.append(('title', {'text': 'EDRN LabCAS User Profile Service'}))
        home_page.body.append(('rich_text', RichText('<p>Welcome to Project: BioKey</p>')))
        home_page.body.append(('rich_text', RichText('<p><em>This is a work in progress.</em></p>')))
        site.root_page = home_page
        old_root.delete()
        mega_root.save()
        home_page.save()
        site.save()
        return site, home_page

    def _set_robots_txt(self, site: Site):
        DisallowedUrl.objects.all().delete()
        Rule.objects.all().delete()

        rule = Rule(robot='*')
        rule.save()
        rule.sites.add(site)
        url = DisallowedUrl(pattern='/')
        rule.disallowed.add(url)
        url.save()
        rule.save()

    def handle(self, *args, **options):
        self.stdout.write('Blooming "BioKey" site')

        try:
            settings.WAGTAILREDIRECTS_AUTO_CREATE = False
            settings.WAGTAILSEARCH_BACKENDS['default']['AUTO_UPDATE'] = False

            site, home_page = self.set_site(options['hostname'])
            self._set_robots_txt(site)

        finally:
            settings.WAGTAILREDIRECTS_AUTO_CREATE = True
            settings.WAGTAILSEARCH_BACKENDS['default']['AUTO_UPDATE'] = True
