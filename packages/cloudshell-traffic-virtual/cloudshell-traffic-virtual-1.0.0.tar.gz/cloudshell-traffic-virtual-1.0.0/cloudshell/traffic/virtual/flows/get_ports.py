ATTR_REQUESTED_VNIC_NAME = "Requested vNIC Name"


class GetPortsFlow(object):
    def __init__(self, cs_api, logger):
        """

        :param cs_api:
        :param logger:
        :return:
        """
        self._cs_api = cs_api
        self._logger = logger

    def _get_resource_attribute_value(self, resource, attribute_name):
        """

        :param resource cloudshell.api.cloudshell_api.ResourceInfo:
        :param str attribute_name:
        """
        for attribute in resource.ResourceAttributes:
            if attribute.Name == attribute_name:
                return attribute.Value

    def _find_ports(self, resources, port_model):
        """

        :param resources:
        :param port_model:
        :return:
        """
        ports = {}
        for resource in resources:
            if resource.ResourceModelName == port_model:
                vnic_name = self._get_resource_attribute_value(resource=resource,
                                                               attribute_name=ATTR_REQUESTED_VNIC_NAME)
                ports[vnic_name] = resource
            else:
                ports.update(self._find_ports(resources=resource.ChildResources,
                                              port_model=port_model))
        return ports

    def execute_flow(self, resource_name, port_model):
        """

        :param resource_name:
        :param port_model:
        :rtype: dict[str, PortModel]
        """
        resource = self._cs_api.GetResourceDetails(resource_name)

        return self._find_ports(resources=resource.ChildResources,
                                port_model=port_model)
