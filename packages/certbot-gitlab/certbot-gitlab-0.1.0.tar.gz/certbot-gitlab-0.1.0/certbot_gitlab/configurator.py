"""GitLab Pages certbot installer plugin."""

import os

import zope.component
import zope.interface

from gitlab import Gitlab, GitlabError

from certbot import interfaces
from certbot.plugins import common
from certbot.errors import PluginError

from os import environ


@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class GitLabConfigurator(common.Plugin):
    description = "GitLab Pages plugin."

    def more_info(self):
        return "Installer for GitLab Pages."

    @classmethod
    def add_parser_arguments(cls, add):
        add("token", help="File containing the GitLab access token")
        add("server", default="https://gitlab.com", help="GitLab server url")
        add("config", help="python-gitlab configuration file")
        add("project", help="Name of GitLab project (e.g. user/proj)")

    @property
    def _display(self):
        return zope.component.getUtility(interfaces.IDisplay)

    def prepare(self):
        # Get Gitlab
        self.gl = self._get_gitlab()
        
        # Check auth
        try:
            self.gl.auth()
        except GitlabError as e:
            raise PluginError("GitLab authentication failed")
        
        # Get project if specified
        project = self.conf("project")
        if project:
            try:
                self.project = self.gl.projects.get(project)
            except GitlabError as e:
                raise PluginError("Could not find project: " + project)
        else:
            self.project = None

    def _get_gitlab(self):
        server = self.conf("server")
        config = self.conf("config")
        
        if config:
            # Create from config file
            Gitlab.from_config(server, [config])
        else:
            # Create from token
            return Gitlab(server, private_token=self._get_gitlab_token())

    def _get_gitlab_token(self):
        token = self.conf("token")
        if not token:
            if "GITLAB_TOKEN" in environ:
                token = environ["GITLAB_TOKEN"]
            else:
                code, token = self._display.input("GitLab API token")
                if code != "ok":
                    token = None
        else:
            with open(token) as file:
                token = file.read().strip()
        
        return token

    def get_all_names(self):
        domains = []
        
        if self.project:
            # Get domains for project
            for pd in self.project.pagesdomains.list(all=True):
                domains.append(pd.domain)
        else:
            # Get all the domains of the user's owned projects
            for project in self.gl.projects.list(owned=True, all=True):
                for pd in project.pagesdomains.list(all=True):
                    domains.append(pd.domain)

        return domains

    def deploy_cert(self, domain, cert_path, key_path, chain_path=None, fullchain_path=None):
        # Get the Gitlab domain
        domain = self._get_pages_domain(domain)

        # Hopefully the cert is good enough if fullchain isn't available
        certificate_path = fullchain_path if fullchain_path else cert_path

        # Read the cert and key
        with open(certificate_path) as certificate, open(key_path) as key:
            domain.certificate = certificate.read()
            domain.key = key.read()

        # Update the domain
        domain.save()

    def _get_pages_domain(self, domain):
        if self.project:
            # Get domain
            try:
                return project.pagesdomains.get(domain)
            except GitlabError as e:
                raise PluginError(str(e))
        else:
            # Check each owned project
            for project in self.gl.projects.list(owned=True, all=True):
                # Check each domain
                for pd in project.pagesdomains.list(all=True):
                    # Return domain if found
                    if pd.domain == domain:
                        return pd
            raise PluginError("Can't find project for domain '%s'" % domain)

    # Unused

    def enhance(self, domain, enhancement, options=None):
        pass

    def supported_enhancements(self):
        return []

    def save(self, title=None, temporary=False):
        pass

    def rollback_checkpoints(self, rollback=1):
        pass

    def recovery_routine(self):
        pass

    def view_config_changes(self):
        pass

    def config_test(self):
        pass

    def restart(self):
        pass
