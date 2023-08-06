
from pnc_cli.swagger_client import BpmApi
from pnc_cli.swagger_client import BuildrecordpushApi
from pnc_cli.swagger_client import BuildrecordsApi
from pnc_cli.swagger_client import BuildsApi
from pnc_cli.swagger_client import BuildconfigsetrecordsApi
from pnc_cli.swagger_client import BuildconfigurationsApi
from pnc_cli.swagger_client import BuildconfigurationsetsApi
from pnc_cli.swagger_client import EnvironmentsApi
from pnc_cli.swagger_client import LicensesApi
from pnc_cli.swagger_client import ProductmilestonesApi
from pnc_cli.swagger_client import ProductreleasesApi
from pnc_cli.swagger_client import ProductsApi
from pnc_cli.swagger_client import ProductversionsApi
from pnc_cli.swagger_client import ProjectsApi
from pnc_cli.swagger_client import RepositoryconfigurationsApi
from pnc_cli.swagger_client import RunningbuildrecordsApi
from pnc_cli.swagger_client import UsersApi
import pnc_cli.user_config as uc


class PncApi:
    
    def __init__(self):
        self._user = None
        self._projects = None
        self._bpm = None
        self._envs = None

    @property
    def user(self):
        if not self._user:
            self._user = uc.user
        return self._user

    @property
    def bpm(self):
        if not self._bpm:
            self._bpm = ProjectsApi(self.user.get_api_client())
        return self._bpm

    @property
    def environments(self):
        if not self._environments:
            self._environments = ProjectsApi(self.user.get_api_client())
        return self._environments

    @property
    def build_push(self):
        if not self._build_push:
            self._build_push = ProjectsApi(self.user.get_api_client())
        return self._build_push

    @property
    def builds(self):
        if not self._builds:
            self._builds = ProjectsApi(self.user.get_api_client())
        return self._builds

    @property
    def build_configs(self):
        if not self._build_configs:
            self._build_configs = ProjectsApi(self.user.get_api_client())
        return self._build_configs

    @property
    def build_group_configs(self):
        if not self._build_group_configs:
            self._build_group_configs = ProjectsApi(self.user.get_api_client())
        return self._build_group_configs

    @property
    def build_groups(self):
        if not self._build_groups:
            self._build_groups = ProjectsApi(self.user.get_api_client())
        return self._build_groups

    @property
    def repositories(self):
        if not self._repositories:
            self._repositories = ProjectsApi(self.user.get_api_client())
        return self._repositories

    @property
    def product_versions(self):
        if not self._product_versions:
            self._product_versions = ProjectsApi(self.user.get_api_client())
        return self._product_versions

    @property
    def products(self):
        if not self._products:
            self._products = ProjectsApi(self.user.get_api_client())
        return self._products

    @property
    def builds_running(self):
        if not self._builds_running:
            self._builds_running = BuildsApi()
        return self._builds_running

    @property
    def running_builds(self):
        if not self._running_builds:
            self._running_builds = ProjectsApi(self.user.get_api_client())
        return self._running_builds

    @property
    def users(self):
        if not self._users:
            self._users = ProjectsApi(self.user.get_api_client())
        return self._users

    @property
    def projects(self):
        if not self._projects:
            self._projects = ProjectsApi(self.user.get_api_client())
        return self._projects

pnc_api = PncApi()
