# encoding: utf-8

'''🧬🔑 BioKey: site bloomer.'''


from django.conf import settings
from django.core.management.base import BaseCommand
from jpl.edrn.biokey.content.models import HomePage
from jpl.edrn.biokey.usermgmt.models import DirectoryInformationTree, EDRNDirectoryInformationTree
from robots.models import Rule, DisallowedUrl
from wagtail.models import Site
from wagtail.rich_text import RichText
import argparse, os, ldap


class Command(BaseCommand):
    help = 'Blooms BioKey with initial content'
    _hostname = 'edrn.jpl.nasa.gov'
    _description = 'User profile management for cancer biomarker applications'
    _seo_title = 'EDRN BioKey User Profile Management'
    _ldap_uri = 'ldaps://edrn-ds.jpl.nasa.gov'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--hostname', help='Hostname of the site (default: %(default)s)', default=self._hostname)
        parser.add_argument('--ldap-uri', help='URI of EDRN LDAP (default: %(default)s)', default=self._ldap_uri)

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

    def _add_dits(self, parent, uri, password):
        self.stdout.write('Deleting any existing DITs')
        DirectoryInformationTree.objects.child_of(parent).delete()
        parent.refresh_from_db()

        for slug, name, user_base, group_base in (
            ('mcl', 'Consortium for Molecular and Cellular Characterization of Screen-Detected Lesions', 'ou=users,o=MCL', 'ou=groups,o=MCL'),
            ('nist', 'National Institutes of Standards and Technology', 'ou=users,o=NIST', 'ou=groups,o=NIST'),
        ):
            dit = DirectoryInformationTree(
                title=name, manager_dn='uid=admin,ou=system', manager_password=password, uri=uri, slug=slug,
                user_base=user_base, user_scope=ldap.SCOPE_ONELEVEL, group_base=group_base,
                group_scope=ldap.SCOPE_ONELEVEL
            )
            parent.add_child(instance=dit)
            dit.save()
            self.stdout.write(f'Added DIT for «{name}»')

        dit = EDRNDirectoryInformationTree(
            title='Early Detection Research Network', manager_password=password, uri=uri, slug='edrn',
            user_base='dc=edrn,dc=jpl,dc=nasa,dc=gov', user_scope=ldap.SCOPE_ONELEVEL,
            group_base='dc=edrn,dc=jpl,dc=nasa,dc=gov', group_scope=ldap.SCOPE_ONELEVEL
        )
        parent.add_child(instance=dit)
        self.stdout.write('Added DIT for «Early Detection Research Network»')
        dit.save()

    def handle(self, *args, **options):
        self.stdout.write('Blooming "BioKey" site')

        try:
            settings.WAGTAILREDIRECTS_AUTO_CREATE = False
            settings.WAGTAILSEARCH_BACKENDS['default']['AUTO_UPDATE'] = False

            site, home_page = self.set_site(options['hostname'])
            self._set_robots_txt(site)
            password = os.getenv('DEFAULT_LDAP_SERVER_PASSWORD')
            if password:
                self._add_dits(home_page, options['ldap_uri'], password)
            else:
                self.stderr.write('No DEFAULT_LDAP_SERVER_PASSWORD set so not adding any DITs')

        finally:
            settings.WAGTAILREDIRECTS_AUTO_CREATE = True
            settings.WAGTAILSEARCH_BACKENDS['default']['AUTO_UPDATE'] = True
