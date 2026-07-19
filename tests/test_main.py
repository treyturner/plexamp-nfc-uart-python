import os
import unittest
from unittest import mock

import main


class FakePort:
    def __init__(
        self,
        device,
        product=None,
        description=None,
        vid=None,
        pid=None,
    ):
        self.device = device
        self.product = product
        self.description = description
        self.vid = vid
        self.pid = pid


class FakeSerial:
    def __init__(self):
        self.dtr = True
        self.rts = True
        self.port = None
        self.opened = False

    def open(self):
        self.opened = True


class ReaderDiscoveryTests(unittest.TestCase):
    def find(self, ports, configured_port=""):
        with mock.patch.dict(os.environ, {"PN532_PORT": configured_port}):
            with mock.patch.object(
                main.list_ports,
                "comports",
                return_value=ports,
            ):
                return main.find_uart_device()

    def test_configured_port_takes_precedence(self):
        ports = [
            FakePort("COM3", vid=0x1A86, pid=0x55D3),
            FakePort("COM5"),
        ]

        result = self.find(ports, "  COM5  ")

        self.assertEqual(result.device, "COM5")
        self.assertFalse(result.is_pn532killer)

    def test_configured_windows_port_matches_case_insensitively(self):
        ports = [FakePort("COM3", vid=0x1A86, pid=0x55D3)]

        result = self.find(ports, "com3")

        self.assertEqual(result.device, "COM3")
        self.assertTrue(result.is_pn532killer)

    def test_unenumerated_configured_port_is_used_as_standard_reader(self):
        result = self.find([], "/dev/cu.usbserial-manual")

        self.assertEqual(result.device, "/dev/cu.usbserial-manual")
        self.assertFalse(result.is_pn532killer)

    def test_killer_is_detected_with_cross_platform_device_names(self):
        for device in ("COM3", "/dev/cu.usbmodem1101"):
            with self.subTest(device=device):
                result = self.find([
                    FakePort(device, product="PN532Killer-UART"),
                ])

                self.assertEqual(result.device, device)
                self.assertTrue(result.is_pn532killer)

    def test_generic_non_linux_ports_are_not_selected_automatically(self):
        ports = [
            FakePort("COM5", product="USB Serial Port"),
            FakePort("/dev/cu.usbserial-110", product="USB Serial Port"),
        ]

        self.assertIsNone(self.find(ports))

    def test_linux_ports_prefer_ttyusb_and_sort_by_device(self):
        ports = [
            FakePort("/dev/ttyUSB1"),
            FakePort("/dev/ttyACM0"),
            FakePort("/dev/ttyUSB0"),
        ]

        result = self.find(ports)

        self.assertEqual(result.device, "/dev/ttyUSB0")
        self.assertFalse(result.is_pn532killer)

    def test_linux_ttyacm_is_used_when_no_ttyusb_exists(self):
        ports = [FakePort("/dev/ttyACM1"), FakePort("/dev/ttyACM0")]

        result = self.find(ports)

        self.assertEqual(result.device, "/dev/ttyACM0")
        self.assertFalse(result.is_pn532killer)


class OpenReaderTests(unittest.TestCase):
    def test_standard_reader_keeps_default_status_lines(self):
        serial_port = FakeSerial()
        reader = mock.Mock()
        reader_class = mock.Mock(return_value=reader)

        with mock.patch.object(
            main.serial,
            "Serial",
            return_value=serial_port,
        ):
            with mock.patch.object(main, "PlexampPN532_UART", reader_class):
                result = main.open_reader(main._ReaderPort("COM5", False))

        self.assertIs(result, reader)
        self.assertEqual(serial_port.port, "COM5")
        self.assertTrue(serial_port.opened)
        self.assertTrue(serial_port.dtr)
        self.assertTrue(serial_port.rts)
        reader_class.assert_called_once_with(serial_port, debug=False)
        reader.SAM_configuration.assert_called_once_with()

    def test_killer_reader_deasserts_status_lines(self):
        serial_port = FakeSerial()
        reader = mock.Mock()
        reader_class = mock.Mock(return_value=reader)

        with mock.patch.object(
            main.serial,
            "Serial",
            return_value=serial_port,
        ):
            with mock.patch.object(main, "PN532Killer_UART", reader_class):
                result = main.open_reader(main._ReaderPort("COM3", True))

        self.assertIs(result, reader)
        self.assertEqual(serial_port.port, "COM3")
        self.assertTrue(serial_port.opened)
        self.assertFalse(serial_port.dtr)
        self.assertFalse(serial_port.rts)
        reader_class.assert_called_once_with(serial_port, debug=False)
        reader.SAM_configuration.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
