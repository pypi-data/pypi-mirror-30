from cloudshell.cli.cli_service_impl import CliServiceImpl
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.devices.cli_handler_impl import CliHandlerImpl

from cloudshell.traffic.teravm.cli import ctrl_command_templates
from cloudshell.traffic.teravm.cli.ctrl_command_modes import CliCommandMode
from cloudshell.traffic.teravm.cli.ctrl_command_modes import DefaultCommandMode


class TeraVMControllerCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        """

        :param cloudshell.cli.cli.CLI cli: CLI object
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api: cloudshell API object
        """
        super(TeraVMControllerCliHandler, self).__init__(cli, resource_config, logger, api)
        self._modes = CommandModeHelper.create_command_mode()

    def on_session_start(self, session, logger):
        """

        :param session:
        :param logger:
        :return:
        """
        # open automation authorization if needed
        test_password = self._api.DecryptPassword(self.resource_config.test_user_password).Value

        if test_password:
            cli_service = CliServiceImpl(session=session, command_mode=self.default_mode, logger=logger)
            command = CommandTemplateExecutor(cli_service=cli_service,
                                              command_template=ctrl_command_templates.OPEN_AUTOMATION_AUTHORIZATION,
                                              action_map={
                                                  "[Pp]assword for user":
                                                      lambda session, logger: session.send_line(
                                                          test_password, logger)
                                              })

            command.execute_command(test_user=self.resource_config.test_user)

    @property
    def default_mode(self):
        return self._modes[DefaultCommandMode]

    @property
    def cli_mode(self):
        return self._modes[CliCommandMode]

    @property
    def enable_mode(self):
        return self.default_mode

    @property
    def config_mode(self):
        return self.default_mode
