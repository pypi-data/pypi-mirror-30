import unittest
import uuid

import jsonpickle
from cloudshell.core.driver_request import DriverRequest
from cloudshell.networking.apply_connectivity.models.connectivity_request import ActionTarget, AttributeNameValue, \
    ConnectionParams, ConnectivityActionRequest
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivitySuccessResponse
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivityErrorResponse
from cloudshell.networking.apply_connectivity.apply_connectivity_operation import apply_connectivity_changes
from mock import Mock, MagicMock


class DriverRequestSimulation:
    def __init__(self, request):
        self.driverRequest = request


class TestApplyConnectivityOperation(unittest.TestCase):
    def setUp(self):
        self.logger = Mock()

    def test_it_delegates_all_add_vlan_calls_to_supplied_callback(self):
        unique_message = 'Unique Result'

        add_vlan_function = MagicMock(side_effect=lambda action: ConnectivitySuccessResponse(action, unique_message))

        # Arrange
        set_vlan_action = self._stub_set_vlan_action(full_address='192.1.3.4/1', full_name='res1/port1', vlan_id='200')

        server_request = DriverRequest()
        server_request.actions = [set_vlan_action]
        request_json = jsonpickle.encode(DriverRequestSimulation(server_request), unpicklable=False)

        # Act
        result = apply_connectivity_changes(request=request_json,
                                            logger=self.logger,
                                            add_vlan_action=add_vlan_function,
                                            remove_vlan_action={})

        # Assert
        add_vlan_function.assert_called_once()
        response = result.driverResponse
        """:type : DriverResponse """
        action_results = response.actionResults
        """:type : list[ConnectivityActionResult] """

        # We validate that the action was delegated by looking for th eunique value we returned
        self.assertEqual(action_results[0].infoMessage, unique_message)

    def test_it_delegates_all_remove_vlan_calls_to_supplied_callback(self):
        unique_message = 'Unique Result'

        remove_vlan_function = MagicMock(side_effect=lambda action: ConnectivitySuccessResponse(action, unique_message))

        # Arrange
        remove_vlan_action = self._stub_remove_vlan_action(full_address='192.1.3.4/1', full_name='res1/port1', vlan_id='200')

        server_request = DriverRequest()
        server_request.actions = [remove_vlan_action]
        request_json = jsonpickle.encode(DriverRequestSimulation(server_request), unpicklable=False)

        # Act
        result = apply_connectivity_changes(request=request_json,
                                            logger=self.logger,
                                            add_vlan_action={},
                                            remove_vlan_action=remove_vlan_function)

        # Assert
        remove_vlan_function.assert_called_once()
        response = result.driverResponse
        """:type : DriverResponse """
        action_results = response.actionResults
        """:type : list[ConnectivityActionResult] """

        # We validate that the action was delegated by looking for th eunique value we returned
        self.assertEqual(action_results[0].infoMessage, unique_message)

    def test_it_merges_the_result_of_all_callbacks_to_one_result_object(self):
        unique_message = 'Unique Result'

        add_vlan_function = MagicMock(side_effect=lambda action: ConnectivitySuccessResponse(action, unique_message))

        # Arrange
        set_vlan_action_1 = self._stub_set_vlan_action(full_address='192.1.3.4/1', full_name='res1/port1',
                                                       vlan_id='200')
        set_vlan_action_2 = self._stub_set_vlan_action(full_address='192.1.3.4/2', full_name='res1/port2',
                                                       vlan_id='201')
        set_vlan_action_3 = self._stub_set_vlan_action(full_address='192.1.3.4/3', full_name='res1/port3',
                                                       vlan_id='202')
        set_vlan_action_4 = self._stub_set_vlan_action(full_address='192.1.3.4/4', full_name='res1/port4',
                                                       vlan_id='203')

        server_request = DriverRequest()
        server_request.actions = [
            set_vlan_action_1,
            set_vlan_action_2,
            set_vlan_action_3,
            set_vlan_action_4
        ]
        request_json = jsonpickle.encode(DriverRequestSimulation(server_request), unpicklable=False)

        # Act
        result = apply_connectivity_changes(request=request_json,
                                            logger=self.logger,
                                            add_vlan_action=add_vlan_function,
                                            remove_vlan_action=[])

        # Assert
        add_vlan_function.assert_called()
        # We validate that the action was delegated by looking for th eunique value we returned
        response = result.driverResponse
        """:type : DriverResponse """
        action_results = response.actionResults
        """:type : list[ConnectivityActionResult] """
        self.assertEqual(len(action_results), 4)
        for result in action_results:
            self.assertEqual(result.infoMessage, unique_message)

    @staticmethod
    def _stub_set_vlan_action(full_address='192.1.3.4/1', full_name='rest1/port1', vlan_id='200'):
        action = ConnectivityActionRequest()
        action.actionId = str(uuid.uuid4())
        action.type = ConnectivityActionRequest.SET_VLAN
        action.actionTarget = ActionTarget(full_address=full_address,
                                           full_name=('%s' % full_name))
        action.connectionId = str(uuid.uuid4())
        action.connectionParams = ConnectionParams(mode='Access', vlan_id=vlan_id,
                                                   vlan_service_attributes=[
                                                       AttributeNameValue(attribute_name='QNQ',
                                                                          attribute_value='false')
                                                   ])
        action.connectorAttributes = []
        action.customActionAttributes = []
        return action

    @staticmethod
    def _stub_remove_vlan_action(full_address='192.1.3.4/1', full_name='rest1/port1', vlan_id='200'):
        action = ConnectivityActionRequest()
        action.actionId = str(uuid.uuid4())
        action.type = ConnectivityActionRequest.REMOVE_VLAN
        action.actionTarget = ActionTarget(full_address=full_address,
                                           full_name=('%s' % full_name))
        action.connectionId = str(uuid.uuid4())
        action.connectionParams = ConnectionParams(mode='Access', vlan_id=vlan_id,
                                                   vlan_service_attributes=[
                                                       AttributeNameValue(attribute_name='QNQ',
                                                                          attribute_value='false')
                                                   ])
        action.connectorAttributes = []
        action.customActionAttributes = []
        return action
