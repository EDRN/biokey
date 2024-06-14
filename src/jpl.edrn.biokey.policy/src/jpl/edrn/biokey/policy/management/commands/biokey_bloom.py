# encoding: utf-8

'''🧬🔑 BioKey: site bloomer.'''


from jpl.edrn.biokey.content.models import HomePage
from jpl.edrn.biokey.usermgmt.models import (
    DirectoryInformationTree, EDRNDirectoryInformationTree, NameRequestFormPage, EmailSettings,
    ForgottenDetailsFormPage, PasswordSettings, PasswordChangeFormPage
)
from jpl.edrn.biokey.theme.models import ColophonSettings

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from robots.models import Rule, DisallowedUrl
from wagtail.images.models import Image
from wagtail.models import Site
from wagtail.rich_text import RichText
import argparse, os, ldap, importlib.resources


class Command(BaseCommand):
    help = 'Blooms BioKey with initial content'
    _hostname = 'edrn.jpl.nasa.gov'
    _port = 80
    _description = 'User profile management for cancer biomarker applications'
    _seo_title = 'EDRN BioKey User Profile Management'
    _ldap_uri = 'ldaps://edrn-ds.jpl.nasa.gov'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--hostname', help='Hostname of the site (default: %(default)s)', default=self._hostname)
        parser.add_argument('--port', help='Port of the site (default %(default)s)', default=self._port, type=int)
        parser.add_argument('--ldap-uri', help='URI of EDRN LDAP (default: %(default)s)', default=self._ldap_uri)

    def set_site(self, hostname: str, port: int):
        '''Set up the Wagtail `Site` object for BioKey.'''

        self.stdout.write('Setting up Wagtail "Site" object')
        site = Site.objects.filter(is_default_site=True).first()
        site.site_name, site.hostname, site.port = 'BioKey', hostname, port
        site.save()
        old_root = site.root_page.specific
        if old_root.title == 'BioKey':
            return site, old_root

        mega_root = old_root.get_parent()

        self.stdout.write('Creating home page')
        home_page = HomePage(
            title='BioKey', draft_title='🧬🔑 BioKey', seo_title=self._seo_title,
            search_description=self._description.strip(), live=True, slug=old_root.slug, path=old_root.path,
            depth=old_root.depth, url_path=old_root.url_path,
        )
        home_page.body.append(('title', {'text': 'EDRN LabCAS User Profile Service'}))
        home_page.body.append(('rich_text', RichText('<p>Welcome to Project: BioKey</p>')))
        home_page.body.append(('rich_text', RichText('<p><em>This is a work in progress.</em></p>')))
        home_page.body.append(('rich_text', RichText('<ul><li><a href="edrn">EDRN</a></li><li><a href="mcl">MCL</a></li><li><a href="nist">NIST</a></li></ul>')))
        site.root_page = home_page
        old_root.delete()
        mega_root.save()
        home_page.save()
        site.save()
        return site, home_page

    def _set_robots_txt(self, site: Site):
        self.stdout.write('Setting up robots.txt')
        DisallowedUrl.objects.all().delete()
        Rule.objects.all().delete()

        rule = Rule(robot='*')
        rule.save()
        rule.sites.add(site)
        url = DisallowedUrl(pattern='/')
        rule.disallowed.add(url)
        url.save()
        rule.save()

    def _add_forms_to_dit(self, dit):
        name_request = NameRequestFormPage(
            title="EDRN Sign Up", slug='sign-up',
            intro=RichText("<p>To get started, let's get your details.</p>")
        )
        dit.add_child(instance=name_request)
        name_request.save()
        changepw = PasswordChangeFormPage(
            title='Change Password', slug='change-password',
            intro=RichText("<p>To change your password, just fill out the form below. <a href='../forgotten'>Can't remember your current password or user ID</a>?")
        )
        dit.add_child(instance=changepw)
        changepw.save()
        forgotten = ForgottenDetailsFormPage(
            title='EDRN: Forgotten Account Details', slug='forgotten',
            intro=RichText("<p>You can use this form if you've forgotten your password or even your username.</p>")
        )
        dit.add_child(instance=forgotten)
        forgotten.save()

    def _add_logo(self, dit: DirectoryInformationTree, logo_fn: str):
        from . import data
        with importlib.resources.open_binary(data, logo_fn) as io:
            image_file = ImageFile(io, name=dit.slug.upper())
            image = Image(title=dit.title, file=image_file)
            image.save()
            dit.logo = image

    def _add_dits(self, parent, uri, password):
        self.stdout.write('Deleting any existing DITs')
        DirectoryInformationTree.objects.child_of(parent).delete()
        parent.refresh_from_db()

        for slug, name, title, user_base, group_base, help_address, logo_fn in (
            ('mcl', 'Consortium for Molecular and Cellular Characterization of Screen-Detected Lesions', 'MCL Password Management', 'ou=users,o=MCL', 'ou=groups,o=MCL', 'ic-data@jpl.nasa.gov', 'mcl.png'),
            ('nist', 'National Institutes of Standards and Technology', 'NIST Password Management', 'ou=users,o=NIST', 'ou=groups,o=NIST', 'ic-data@jpl.nasa.gov', 'nist.png'),
        ):
            self.stdout.write(f'Creating DIT for {name}')
            dit = DirectoryInformationTree(
                title=name, page_title=title, manager_dn='uid=admin,ou=system', manager_password=password, uri=uri,
                slug=slug, user_base=user_base, user_scope=ldap.SCOPE_ONELEVEL, group_base=group_base,
                group_scope=ldap.SCOPE_ONELEVEL, help_address=help_address
            )
            parent.add_child(instance=dit)
            self._add_forms_to_dit(dit)
            self._add_logo(dit, logo_fn)
            dit.save()
            self.stdout.write(f'Added DIT for «{name}»')

        self.stdout.write('Creating DIT for EDRN')
        dit = EDRNDirectoryInformationTree(
            title='Early Detection Research Network', manager_password=password, uri=uri, slug='edrn',
            page_title='EDRN Password Management',
            user_base='dc=edrn,dc=jpl,dc=nasa,dc=gov', user_scope=ldap.SCOPE_ONELEVEL,
            group_base='dc=edrn,dc=jpl,dc=nasa,dc=gov', group_scope=ldap.SCOPE_ONELEVEL,
            help_address='edrn-ic@jpl.nasa.gov'
        )
        parent.add_child(instance=dit)
        self._add_forms_to_dit(dit)
        self._add_logo(dit, 'edrn.png')
        self.stdout.write('Added DIT for «Early Detection Research Network»')
        dit.save()

    def _set_settings(self, site):
        self.stdout.write('Creating email settings')
        email = EmailSettings.objects.get_or_create(site_id=site.id)[0]
        email.from_address = 'no-reply@jpl.nasa.gov'
        email.new_users_address = 'edrn-ic@jpl.nasa.gov'
        email.save()

        self.stdout.write('Creating password settings')
        password = PasswordSettings.objects.get_or_create(site_id=site.id)[0]
        password.reset_window = 4320
        password.save()

        self.stdout.write('Creating colophon settings')
        colophon = ColophonSettings.objects.get_or_create(site_id=site.id)[0]
        colophon.save()

    def handle(self, *args, **options):
        self.stdout.write('Blooming "BioKey" site')

        try:
            settings.WAGTAILREDIRECTS_AUTO_CREATE = False
            settings.WAGTAILSEARCH_BACKENDS['default']['AUTO_UPDATE'] = False

            site, home_page = self.set_site(options['hostname'], options['port'])
            self._set_robots_txt(site)
            self._set_settings(site)
            password = os.getenv('DEFAULT_LDAP_SERVER_PASSWORD')
            if password:
                self._add_dits(home_page, options['ldap_uri'], password)
            else:
                self.stderr.write('No DEFAULT_LDAP_SERVER_PASSWORD set so not adding any DITs')

        finally:
            settings.WAGTAILREDIRECTS_AUTO_CREATE = True
            settings.WAGTAILSEARCH_BACKENDS['default']['AUTO_UPDATE'] = True
