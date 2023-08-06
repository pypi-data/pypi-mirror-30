import unittest

from cloudshell.networking.networking_resource_driver_interface import NetworkingResourceDriverInterface


class TestNetworkingResourceDriverInterface(unittest.TestCase):
    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        class TestedClass(NetworkingResourceDriverInterface):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with abstract methods "
                                                "ApplyConnectivityChanges, get_inventory, health_check, load_firmware, "
                                                "orchestration_restore, orchestration_save, restore, "
                                                "run_custom_command, run_custom_config_command, save, shutdown"):
            TestedClass()
