"""
test_pysoundio.py

PySoundIo Test Suite
"""
import ctypes
import unittest
import pysoundio


class TestPySoundIo(unittest.TestCase):

    def setUp(self):
        self.sio = pysoundio.PySoundIo(
            backend=pysoundio.SoundIoBackendDummy)
        self.sio.channels = 2
        self.sio.sample_rate = 44100
        self.sio.format = pysoundio.SoundIoFormatFloat32LE
        self.sio.block_size = None

    def tearDown(self):
        self.sio.close()

    def test_version(self):
        self.assertIsInstance(self.sio.version, str)

    def test_backend_count(self):
        self.assertIsInstance(self.sio.backend_count, int)

    def test_get_default_input_device(self):
        self.assertIsNotNone(self.sio.get_default_input_device())

    def test_get_input_device(self):
        self.assertIsNotNone(self.sio.get_input_device(0))

    def test_get_default_output_device(self):
        self.assertIsNotNone(self.sio.get_default_output_device())

    def test_get_output_device(self):
        self.assertIsNotNone(self.sio.get_output_device(0))

    def test_list_devices(self):
        input_devices, output_devices = self.sio.list_devices()
        self.assertIsInstance(input_devices, list)
        self.assertIsInstance(output_devices, list)
        self.assertTrue(len(input_devices) > 0)
        self.assertTrue(len(output_devices) > 0)
        self.assertIsInstance(input_devices[0], dict)
        self.assertIsInstance(output_devices[0], dict)
        self.assertIn('id', input_devices[0])
        self.assertIn('name', input_devices[0])
        self.assertIn('is_raw', input_devices[0])
        self.assertIn('id', output_devices[0])
        self.assertIn('name', output_devices[0])
        self.assertIn('is_raw', output_devices[0])

    def test_supports_sample_rate(self):
        device = self.sio.get_input_device(0)
        self.assertTrue(self.sio.supports_sample_rate(device, 44100))

    def test_get_default_sample_rate(self):
        device = self.sio.get_input_device(0)
        self.sio.get_default_sample_rate(device)
        self.assertIsNotNone(self.sio.sample_rate)

    def test_supports_format(self):
        device = self.sio.get_input_device(0)
        self.assertTrue(self.sio.supports_format(device, pysoundio.SoundIoFormatFloat32LE))

    def test_get_default_format(self):
        device = self.sio.get_input_device(0)
        self.sio.get_default_format(device)
        self.assertIsNotNone(self.sio.format)

    def test_get_default_layout(self):
        self.assertIsNotNone(self.sio._get_default_layout(2))


    def test_bytes_per_frame(self):
        self.assertEqual(pysoundio.get_bytes_per_frame(
            pysoundio.SoundIoFormatFloat32LE, 2), 8)

    def test_bytes_per_sample(self):
        self.assertEqual(pysoundio.get_bytes_per_sample(
            pysoundio.SoundIoFormatFloat32LE), 4)

    def test_bytes_per_second(self):
        self.assertEqual(pysoundio.get_bytes_per_second(
            pysoundio.SoundIoFormatFloat32LE, 1, 44100), 176400)


    def test_create_input_ring_buffer(self):
        capacity = 44100 * 8
        self.assertIsNotNone(self.sio._create_input_ring_buffer(capacity))

    def test_create_input_stream(self):
        self.sio.get_default_input_device()
        stream = self.sio._create_input_stream()
        self.assertIsNotNone(stream)

    def test_open_input_stream(self):
        self.sio.get_default_input_device()
        stream = self.sio._create_input_stream()
        self.sio._open_input_stream()

    def test_start_input_stream(self):
        self.sio.start_input_stream(
            sample_rate=44100,
            dtype=pysoundio.SoundIoFormatFloat32LE,
            channels=2)
        self.assertIsNotNone(self.sio.input_stream)

    def test_create_output_stream(self):
        self.sio.get_default_output_device()
        stream = self.sio._create_output_stream()
        self.assertIsNotNone(stream)

    def test_open_output_stream(self):
        self.sio.get_default_output_device()
        stream = self.sio._create_output_stream()
        self.sio._open_output_stream()
        self.assertIsNotNone(self.sio.block_size)

    def test_start_output_stream(self):
        self.sio.get_default_output_device()
        stream = self.sio._create_output_stream()
        self.sio._open_output_stream()

        pyoutstream = ctypes.cast(stream, ctypes.POINTER(pysoundio.SoundIoOutStream))
        pyoutstream.contents.format = pysoundio.SoundIoFormatFloat32LE
        pyoutstream.contents.sample_rate = 44100

        self.sio._start_output_stream()
