import itertools

from cloudshell.api.cloudshell_api import AttributeNameValue
from cloudshell.api.cloudshell_api import SetConnectorRequest


ATTR_REQUESTED_SOURCE_VNIC = "Requested Source vNIC Name"
ATTR_REQUESTED_TARGET_VNIC = "Requested Target vNIC Name"


class ConnectChildResourcesFlow(object):
    def __init__(self, logger, cs_api):
        """

        :param logger:
        :param cs_api:
        :return:
        """
        self._logger = logger
        self._cs_api = cs_api

    def execute_flow(self, connectors, ports, resource_name, reservation_id):
        if not connectors:
            return "Success"

        new_connectors_data = []
        to_disconnect = []

        for connector in connectors:
            source_remap_vnics = connector.attributes.get(ATTR_REQUESTED_SOURCE_VNIC, "").split(",")
            target_remap_vnics = connector.attributes.get(ATTR_REQUESTED_TARGET_VNIC, "").split(",")

            source = connector.source
            target = connector.target

            # remove old connector
            to_disconnect.extend([source, target])

            if resource_name in connector.source.split("/"):
                is_source = True
            else:
                is_source = False

            for source_vnic, target_vnic in itertools.izip_longest(source_remap_vnics, target_remap_vnics):
                new_connector_data = self._create_connector_data(is_source=is_source,
                                                                 source_vnic=source_vnic,
                                                                 target_vnic=target_vnic,
                                                                 ports=ports,
                                                                 connector=connector)
                new_connectors_data.append(new_connector_data)

        self._cs_api.RemoveConnectorsFromReservation(reservation_id, to_disconnect)

        new_connectors = []
        for connector_data in new_connectors_data:
            conn = SetConnectorRequest(SourceResourceFullName=connector_data.source,
                                       TargetResourceFullName=connector_data.target,
                                       Direction=connector_data.direction,
                                       Alias=None)
            new_connectors.append(conn)

        self._cs_api.SetConnectorsInReservation(reservation_id, new_connectors)

        for connector_data in new_connectors_data:
            connector_attrs = []

            if connector_data.source_vnic:
                connector_attr = AttributeNameValue(Name=ATTR_REQUESTED_SOURCE_VNIC,
                                                    Value=connector_data.source_vnic)
                connector_attrs.append(connector_attr)

            if connector_data.target_vnic:
                connector_attr = AttributeNameValue(Name=ATTR_REQUESTED_TARGET_VNIC,
                                                    Value=connector_data.target_vnic)
                connector_attrs.append(connector_attr)

            if connector_attrs:
                self._cs_api.SetConnectorAttributes(reservationId=reservation_id,
                                                    sourceResourceFullName=connector_data.source,
                                                    targetResourceFullName=connector_data.target,
                                                    attributeRequests=connector_attrs)

    def _create_connector_data(self, is_source, source_vnic, target_vnic, ports, connector):
        """

        :param is_source:
        :param source_vnic:
        :param target_vnic:
        :param ports:
        :param connector:
        :rtype: ConnectorData
        """
        source = None
        target = None

        if is_source:
            target = connector.target
            if source_vnic:
                port = ports.pop(source_vnic)
                source = port.Name
        else:
            source = connector.source
            if target_vnic:
                port = ports.pop(target_vnic)
                target = port.Name

        return ConnectorData(direction=connector.direction,
                             free_ports=ports,
                             source=source,
                             target=target,
                             source_vnic=source_vnic,
                             target_vnic=target_vnic)


class ConnectorData(object):
    def __init__(self, direction, free_ports, source=None, target=None, source_vnic=None, target_vnic=None):
        """

        :param str direction: connector direction
        :param dict[str, Port] free_ports: free resource ports
        :param str source: source port name
        :param str target: target port name
        :param str source_vnic: source vNIC adapter number
        :param str target_vnic: target vNIC adapter number
        """
        self.direction = direction
        self.source_vnic = source_vnic
        self.target_vnic = target_vnic
        self._source = source
        self._target = target
        self._free_ports = free_ports

    def _get_free_port(self):
        """Get the last port from the free ports dictionary

        :return:
        """
        try:
            vnic_id = self._free_ports.keys()[-1]
        except IndexError:
            raise Exception("No free ports left on the resource")

        return self._free_ports.pop(vnic_id)

    @property
    def source(self):
        if not self._source:
            self._source = self._get_free_port().Name
        return self._source

    @property
    def target(self):
        if not self._target:
            self._target = self._get_free_port().Name
        return self._target
