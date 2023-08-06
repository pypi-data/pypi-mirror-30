import unittest

import mock

from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivityErrorResponse
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivitySuccessResponse


class TestConnectivitySuccessResponse(unittest.TestCase):
    def test_init(self):
        """Check that __init__ nethod will set up object with correct params"""
        action = mock.MagicMock()
        result_string = "info message"

        # act
        response = ConnectivitySuccessResponse(action=action, result_string=result_string)

        # verify
        self.assertEqual(response.type, action.type)
        self.assertEqual(response.actionId, action.actionId)
        self.assertIsNone(response.errorMessage)
        self.assertEqual(response.updatedInterface, action.actionTarget.fullName)
        self.assertEqual(response.infoMessage, result_string)
        self.assertTrue(response.success)


class TestConnectivityErrorResponse(unittest.TestCase):
    def test_init(self):
        """Check that __init__ nethod will set up object with correct params"""
        action = mock.MagicMock()
        err_string = "error message"

        # act
        response = ConnectivityErrorResponse(action=action, error_string=err_string)

        # verify
        self.assertEqual(response.type, action.type)
        self.assertEqual(response.actionId, action.actionId)
        self.assertIsNone(response.infoMessage)
        self.assertEqual(response.updatedInterface, action.actionTarget.fullName)
        self.assertEqual(response.errorMessage, err_string)
        self.assertFalse(response.success)
