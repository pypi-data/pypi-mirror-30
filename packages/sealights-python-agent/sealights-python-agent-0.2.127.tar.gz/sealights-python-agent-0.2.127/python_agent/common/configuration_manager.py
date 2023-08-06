import json
import logging
import os

from python_agent import __file__ as root_directory_module
from python_agent.common.autoupgrade.autoupgrade_manager import AutoUpgrade
from python_agent.common.config_data import ConfigData
from python_agent.common.constants import CONFIG_FILE, BUILD_SESSION_ID_FILE, TOKEN_FILE, CONFIG_ENV_VARIABLE
from python_agent.common.environment_variables_resolver import EnvironmentVariablesResolver
from python_agent.common.http.backend_proxy import BackendProxy
from python_agent.common.log.sealights_logging import SealightsHTTPHandler
from python_agent.common.token.token_parser import TokenParser

log = logging.getLogger(__name__)

# A list off properties, which should be converted to integer
INT_PROPERTIES = ['commitHistoryLength']


class ConfigurationManager(object):

    def __init__(self, config_filename="sealights.json"):
        self.config_filename = config_filename or os.environ.get(CONFIG_FILE)
        self.config_data = ConfigData()
        self.env_resolver = EnvironmentVariablesResolver(INT_PROPERTIES, self.config_data)

    def init_configuration(self, is_config_cmd, token, buildsessionid, tokenfile=TOKEN_FILE, buildsessionidfile=BUILD_SESSION_ID_FILE, proxy=None, scm_args=None):
        token_data, token = self.resolve_token_data(token, tokenfile)
        if not token:
            log.error("--token or --tokenfile must be provided")
            return None

        self.config_data = ConfigData(token, token_data.customerId, token_data.server, proxy)
        if not is_config_cmd:
            build_session_id = self.resolve_build_session_id(buildsessionid, buildsessionidfile)
            self.try_load_configuration(scm_args)
            if not build_session_id:
                log.error("--buildsessionid or --buildsessionidfile must be provided")
                return None
            self.config_data.buildSessionId = build_session_id
            self.update_build_session_data()

        self.init_features()
        return self.config_data

    def try_load_configuration_from_config_environment_variable(self):
        config_data = os.environ.get(CONFIG_ENV_VARIABLE)
        if config_data:
            config_data = json.loads(config_data)
            self.config_data.__dict__.update(config_data)

    def try_load_configuration_from_file(self):
        config_file_path = self.get_default_config_file_path()
        if config_file_path and os.path.isfile(config_file_path):
            with open(config_file_path, "r") as f:
                configuration = f.read()
                configuration = json.loads(configuration)
                self.config_data.__dict__.update(configuration)

    def _try_load_configuration_from_environment_variables(self):
        self.config_data.__dict__.update(self.env_resolver.resolve())
        return self.config_data

    def _try_load_configuration_from_server(self):
        backend_proxy = BackendProxy(self.config_data)
        result = backend_proxy.get_remote_configuration()
        self.config_data.__dict__.update(result)
        return self.config_data

    def init_features(self):
        self.init_logging()
        # self.init_coloring()
        self._upgrade_agent()

    def try_load_configuration(self, scm_args):
        self.try_load_configuration_from_file()
        self.config_data.apply_scm_args(scm_args)
        self._try_load_configuration_from_environment_variables()
        self._try_load_configuration_from_server()

    def update_build_session_data(self):
        backend_proxy = BackendProxy(self.config_data)
        build_session_data = backend_proxy.get_build_session(self.config_data.buildSessionId)
        self.config_data.__dict__.update(build_session_data.__dict__)

    def resolve_token_data(self, token, tokenfile):
        if not token and (not tokenfile or not os.path.isfile(tokenfile)):
            log.warning("tokenfile %s doesn't exist" % (tokenfile))
            log.error("token could not be resolved")
            return None, None
        if not token and tokenfile:
            with open(os.path.abspath(tokenfile), 'r') as f:
                token = f.read()
                token = token.rstrip()
        token_data, token = TokenParser.parse_and_validate(token)
        return token_data, token

    def _upgrade_agent(self):
        auto_upgrade = AutoUpgrade(self.config_data)
        auto_upgrade.upgrade()

    def resolve_build_session_id(self, buildsessionid, buildsessionidfile):
        if buildsessionid:
            return buildsessionid
        if buildsessionidfile and os.path.isfile(buildsessionidfile):
            with open(os.path.abspath(buildsessionidfile), 'r') as f:
                buildsessionid = f.read()
                return buildsessionid.rstrip()
        return None

    def get_default_config_file_path(self):
        root_directory = os.path.dirname(root_directory_module)
        config_file_path = os.path.join(root_directory, self.config_filename)
        return config_file_path

    def init_logging(self):
        if self.config_data.isSendLogs:
            sl_handler = SealightsHTTPHandler(self.config_data, capacity=50)
            sl_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(process)d|%(thread)d] %(name)s: %(message)s')
            sl_handler.setFormatter(sl_formatter)
            agent_logger = logging.getLogger("python_agent")
            agent_logger.addHandler(sl_handler)

    def init_coloring(self):
        self.init_coloring_incoming()
        self.init_coloring_outgoing()

    def init_coloring_outgoing(self):
        pass
        # from python_agent.test_listener.coloring import __all__
        # for coloring_framework_name in __all__:
        #     __import__(
        #         "%s.%s.%s.%s" % ("python_agent", "test_listener", "coloring", coloring_framework_name),
        #         fromlist=[coloring_framework_name]
        #     )
        #     log.debug("Imported Coloring Framework: %s" % coloring_framework_name)
        # log.info("Imported Coloring Frameworks: %s" % __all__)

    def init_coloring_incoming(self):
        from python_agent.test_listener.web_frameworks import __all__
        for web_framework_name in __all__:
            web_framework = __import__(
                "%s.%s.%s.%s" % ("python_agent", "test_listener", "web_frameworks", web_framework_name),
                fromlist=[web_framework_name]
            )
            bootstrap_method = getattr(web_framework, "bootstrap", None)
            if bootstrap_method:
                bootstrap_method()
                log.debug("Bootstrapped Framework: %s" % web_framework_name)
        log.info("Bootstrapped Frameworks: %s" % __all__)


