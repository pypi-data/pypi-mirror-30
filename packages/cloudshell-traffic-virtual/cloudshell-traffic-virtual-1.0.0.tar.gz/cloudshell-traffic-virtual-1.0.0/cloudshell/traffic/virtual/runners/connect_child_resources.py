from cloudshell.traffic.virtual.flows.connect_child_resources import ConnectChildResourcesFlow
from cloudshell.traffic.virtual.flows.get_ports import GetPortsFlow


class ConnectChildResourcesRunner(object):
    def __init__(self, logger, cs_api):
        self._logger = logger
        self._cs_api = cs_api

    @property
    def get_ports_flow(self):
        """

        :rtype: GetPortsFlow
        """
        return GetPortsFlow(logger=self._logger,
                            cs_api=self._cs_api)

    @property
    def connect_child_resources_flow(self):
        """

        :rtype: ConnectChildResourcesFlow
        """
        return ConnectChildResourcesFlow(logger=self._logger,
                                         cs_api=self._cs_api)

    def get_ports(self, resource_name, port_model):
        """

        :param resource_name:
        :param port_model:
        :return:
        """
        return self.get_ports_flow.execute_flow(resource_name=resource_name,
                                                port_model=port_model)

    def connect_child_resources(self, connectors, ports, resource_name, reservation_id):
        """

        :param connectors:
        :param ports:
        :param resource_name:
        :param reservation_id:
        :return:
        """
        return self.connect_child_resources_flow.execute_flow(connectors=connectors,
                                                              ports=ports,
                                                              resource_name=resource_name,
                                                              reservation_id=reservation_id)
