"""
pysoundio.py

Play and Record Sound in Python using libsoundio

libsoundio is a C library for cross-platform audio input and output.
It is suitable for real-time and consumer software.

"""
import logging
import threading

import ctypes as _ctypes
from .constants import (
    DEFAULT_RING_BUFFER_DURATION,
    PRIORITISED_FORMATS,
    PRIORITISED_SAMPLE_RATES,
)
from .structures import (
    SoundIoErrorCallback,
    SoundIoOverflowCallback,
    SoundIoReadCallback,
    SoundIoUnderflowCallback,
    SoundIoWriteCallback,
    SoundIoDevice,
    SoundIoInStream,
    SoundIoOutStream,
    SoundIoChannelLayout,
)
import _soundiox as soundio

LOGGER = logging.getLogger(__name__)


class PySoundIoError(Exception):
    pass


class _InputProcessingThread(threading.Thread):

    def __init__(self, parent, *args, **kwargs):
        self.buffer = parent.input_buffer
        self.callback = parent.read_callback
        self.bytes_per_frame = parent.input_bytes_per_frame
        super(_InputProcessingThread, self).__init__(*args, **kwargs)

    def run(self):
        """ Callback with data """
        fill_bytes = soundio.ring_buffer_fill_count(self.buffer)
        read_buf = soundio.ring_buffer_read_ptr(self.buffer)
        if self.callback and fill_bytes:
            self.callback(data=read_buf, length=fill_bytes / self.bytes_per_frame)
        soundio.ring_buffer_advance_read_ptr(self.buffer, fill_bytes)


class _OutputProcessingThread(threading.Thread):

    def __init__(self, parent, block_size, *args, **kwargs):
        self.buffer = parent.output_buffer
        self.callback = parent.write_callback
        self.bytes_per_frame = parent.output_bytes_per_frame
        self.block_size = block_size
        super(_OutputProcessingThread, self).__init__(*args, **kwargs)

    def run(self):
        """ Callback to fill data """
        data = bytearray(b'\x00' * self.block_size * self.bytes_per_frame)
        free_bytes = soundio.ring_buffer_free_count(self.buffer)
        if self.callback and free_bytes >= len(data):
            self.callback(data=data, length=self.block_size)
        soundio.ring_buffer_write_ptr(self.buffer, data, len(data))
        soundio.ring_buffer_advance_write_ptr(self.buffer, len(data))


class PySoundIo(object):

    def __init__(self, backend=None):
        """
        Initialise PySoundIo.
        Connect to a specific backend, or the default.

        Parameters
        ----------
        backend: (SoundIoBackend) see `Backends`_. (optional)
        """
        self.backend = backend
        self.testing = False

        self.input_device = None
        self.output_device = None
        self.input_stream = None
        self.output_stream = None
        self.input_buffer = None
        self.output_buffer = None
        self.read_callback = None
        self.write_callback = None

        self._soundio = soundio.create()
        if backend:
            soundio.connect_backend(backend)
        else:
            soundio.connect()
        self.flush()

    def close(self):
        """
        Clean up allocated memory
        Close libsoundio connections
        """
        if self.input_stream:
            soundio.instream_destroy()
            self.input_stream = None
        if self.output_stream:
            soundio.outstream_destroy()
            self.output_stream = None
        if self.input_buffer:
            soundio.ring_buffer_destroy(self.input_buffer)
            self.input_buffer = None
        if self.output_buffer:
            soundio.ring_buffer_destroy(self.output_buffer)
            self.output_buffer = None
        if self.input_device:
            soundio.device_unref(self.input_device)
            self.input_device = None
        if self.output_device:
            soundio.device_unref(self.output_device)
            self.output_device = None
        if self._soundio:
            soundio.disconnect()
            soundio.destroy()
            self._soundio = None

    def flush(self):
        """
        Atomically update information for all connected devices.
        """
        soundio.flush()

    @property
    def backend_count(self):
        """
        Returns the number of available backends.
        """
        return soundio.backend_count()

    def get_default_input_device(self):
        """
        Returns default input device

        Returns
        -------
        PySoundIoDevice input device

        Raises
        ------
        PySoundIoError if the input device is not available
        """
        device_id = soundio.default_input_device_index()
        return self.get_input_device(device_id)

    def get_input_device(self, device_id):
        """
        Return an input device by index

        Parameters
        ----------
        device_id: (int) input device index

        Returns
        -------
        PySoundIoDevice input device

        Raises
        ------
        PySoundIoError if an invalid device id is used, or device is unavailable
        """
        if device_id < 0 or device_id > soundio.get_input_device_count():
            raise PySoundIoError('Invalid input device id')
        self.input_device = soundio.get_input_device(device_id)
        return self.input_device

    def get_default_output_device(self):
        """
        Returns default output device

        Returns
        -------
        PySoundIoDevice output device

        Raises
        ------
        PySoundIoError if the output device is not available
        """
        device_id = soundio.default_output_device_index()
        return self.get_output_device(device_id)

    def get_output_device(self, device_id):
        """
        Return an output device by index

        Parameters
        ----------
        device_id: (int) output device index

        Returns
        -------
        PySoundIoDevice output device

        Raises
        ------
        PySoundIoError if an invalid device id is used, or device is unavailable
        """
        if device_id < 0 or device_id > soundio.get_output_device_count():
            raise PySoundIoError('Invalid output device id')
        self.output_device = soundio.get_output_device(device_id)
        return self.output_device

    def list_devices(self):
        """
        Return a list of available devices

        Returns
        -------
        (list)(dict) containing information on available input / output devices.
        """
        output_count = soundio.get_output_device_count()
        input_count = soundio.get_input_device_count()

        default_output = soundio.default_output_device_index()
        default_input = soundio.default_input_device_index()

        input_devices = []
        output_devices = []

        for i in range(0, input_count):
            device = soundio.get_input_device(i)
            pydevice = _ctypes.cast(device, _ctypes.POINTER(SoundIoDevice))
            input_devices.append({
                'id': pydevice.contents.id.decode(), 'name': pydevice.contents.name.decode(),
                'is_raw': pydevice.contents.is_raw, 'is_default': default_input == i
                # TODO: Add more parameters
            })
            soundio.device_unref(device)

        for i in range(0, output_count):
            device = soundio.get_output_device(i)
            pydevice = _ctypes.cast(device, _ctypes.POINTER(SoundIoDevice))
            output_devices.append({
                'id': pydevice.contents.id.decode(), 'name': pydevice.contents.name.decode(),
                'is_raw': pydevice.contents.is_raw, 'is_default': default_output == i
                # TODO: Add more parameters
            })
            soundio.device_unref(device)

        LOGGER.info('%d devices found' % (input_count + output_count))
        return (input_devices, output_devices)

    def supports_sample_rate(self, device, rate):
        """
        Check the sample rate is supported by the selected device.

        Parameters
        ----------
        device: (SoundIoDevice) device object
        rate (int): sample rate

        Returns
        -------
        (bool) True if sample rate is supported for this device
        """
        return soundio.device_supports_sample_rate(device, rate) > 0

    def get_default_sample_rate(self, device):
        """
        Get the best sample rate.

        Parameters
        ----------
        device: (SoundIoDevice) device object

        Returns
        -------
        (int) The best available sample rate
        """
        for rate in PRIORITISED_SAMPLE_RATES:
            if self.supports_sample_rate(device, rate):
                sample_rate = rate
                break
        if not sample_rate:
            pydevice = _ctypes.cast(device, _ctypes.POINTER(SoundIoDevice))
            sample_rate = pydevice.contents.sample_rates.contents.max
        return sample_rate

    def supports_format(self, device, format):
        """
        Check the format is supported by the selected device.

        Parameters
        ----------
        device: (SoundIoDevice) device object
        format: (SoundIoFormat) see `Formats`_.

        Returns
        -------
        (bool) True if the format is supported for this device
        """
        return soundio.device_supports_format(device, format) > 0

    def get_default_format(self, device):
        """
        Get the best format value.

        Parameters
        ----------
        device: (SoundIoDevice) device object

        Returns
        ------
        (SoundIoFormat) The best available format
        """
        for fmt in PRIORITISED_FORMATS:
            if self.supports_format(device, fmt):
                dtype = fmt
                break
        if dtype == soundio.SoundIoFormatInvalid:
            pydevice = _ctypes.cast(device, _ctypes.POINTER(SoundIoDevice))
            dtype = pydevice.formats.contents
        return dtype

    def sort_channel_layouts(self, device):
        """
        Sorts channel layouts by channel count, descending

        Parameters
        ----------
        device: (SoundIoDevice) device object
        """
        soundio.device_sort_channel_layouts(device)

    def _get_default_layout(self, channels):
        """
        Get default builtin channel layout for the given number of channels

        Parameters
        ----------
        channels: (int) desired number of channels
        """
        return soundio.channel_layout_get_default(channels)

    def get_bytes_per_frame(self, device, channels):
        """
        Get the number of bytes per frame

        Parameters
        ----------
        device: (PySoundIoDevice) device
        channels: (int) number of channels

        Returns
        -------
        (int) number of bytes per frame
        """
        return soundio.get_bytes_per_frame(device, channels)

    def get_bytes_per_sample(self, device):
        """
        Get the number of bytes per sample

        Parameters
        ----------
        device: (PySoundIoDevice) device

        Returns
        -------
        (int) number of bytes per sample
        """
        return soundio.get_bytes_per_sample(device)

    def get_bytes_per_second(self, device, channels, sample_rate):
        """
        Get the number of bytes per second

        Parameters
        ----------
        device: (PySoundIoDevice) device
        channels (int) number of channels
        sample_rate (int) sample rate

        Returns
        -------
        (int) number of bytes per second
        """
        return soundio.get_bytes_per_second(device, channels, sample_rate)

    def _create_input_ring_buffer(self, capacity):
        """
        Creates ring buffer with the capacity to hold 30 seconds of data,
        by default.
        """
        self.input_buffer = soundio.input_ring_buffer_create(capacity)
        if not self.input_buffer:
            raise PySoundIoError('Failed to create ring buffer')
        return self.input_buffer

    def _create_output_ring_buffer(self, capacity):
        """
        Creates ring buffer with the capacity to hold 30 seconds of data,
        by default.
        """
        self.output_buffer = soundio.output_ring_buffer_create(capacity)
        if not self.output_buffer:
            raise PySoundIoError('Failed to create ring buffer')
        return self.output_buffer

    def _create_input_stream(self):
        """
        Allocates memory and sets defaults for input stream
        """
        self.input_stream = soundio.instream_create(self.input_device)
        if not self.input_stream:
            raise PySoundIoError('Could not create input stream')

        pyinstream = _ctypes.cast(self.input_stream, _ctypes.POINTER(SoundIoInStream))
        soundio.set_read_callback(self._read_callback)

        layout = self._get_default_layout(self.channels)
        pylayout = _ctypes.cast(layout, _ctypes.POINTER(SoundIoChannelLayout))
        pyinstream.contents.layout = pylayout.contents

        pyinstream.contents.format = self.format
        pyinstream.contents.sample_rate = self.sample_rate
        if self.block_size:
            pyinstream.contents.software_latency = float(self.block_size) / self.sample_rate

        return self.input_stream

    def _open_input_stream(self):
        """
        Open an input stream.
        """
        soundio.instream_open()

    def _start_input_stream(self):
        """
        Start an input stream running.
        """
        soundio.instream_start()

    def pause_input_stream(self, pause):
        """
        Pause input stream

        Parameters
        ----------
        pause: (bool) True to pause, False to unpause
        """
        soundio.instream_pause(pause)

    def get_input_latency(self, out_latency):
        """
        Obtain the number of seconds that the next frame of sound
        being captured will take to arrive in the buffer,
        plus the amount of time that is represented in the buffer.

        Parameters
        ----------
        out_latency: (int) output latency in seconds
        """
        return soundio.instream_get_latency(out_latency)

    def _read_callback(self):
        """
        Internal read callback.
        """
        _InputProcessingThread(parent=self).start()

    def _overflow_callback(self, stream):
        """
        Internal overflow callback, which calls the external
        overflow callback if defined.
        """
        if self.overflow_callback:
            self.overflow_callback(stream)

    def _error_callback(self, stream, err):
        """
        Internal error callback, which calls the external
        error callback if defined.
        """
        if self.error_callback:
            self.error_callback(stream, err)

    def start_input_stream(self, device_id=None,
                           sample_rate=None, dtype=None,
                           block_size=None, channels=None,
                           read_callback=None, overflow_callback=None,
                           error_callback=None):
        """
        Creates input stream, and sets parameters. Then allocates
        a ring buffer and starts the stream.

        The read callback is called in an audio processing thread,
        when a block of data is read from the microphone. Data is
        passed from the ring buffer to the callback to process.

        Parameters
        ----------
        device_id: (int) input device id
        sample_rate: (int) desired sample rate (optional)
        dtype: (SoundIoFormat) desired format, see `Formats`_. (optional)
        block_size: (int) desired block size (optional)
        channels: (int) number of channels [1: mono, 2: stereo] (optional)
        read_callback: (fn) function to call with data, the function must have
                        the arguments data and length. See record example

        Raises
        ------
        PySoundIoError if any invalid parameters are used

        Notes
        -----
        An example read callback

        .. code-block:: python
            :linenos:

            def read_callback(data, length):
                wav.write(data)
        """
        self.sample_rate = sample_rate
        self.format = dtype
        self.block_size = block_size
        self.channels = channels
        self.read_callback = read_callback
        self.overflow_callback = overflow_callback
        self.error_callback = error_callback

        if device_id:
            self.input_device = self.get_input_device(device_id)
        else:
            self.input_device = self.get_default_input_device()

        pydevice = _ctypes.cast(self.input_device, _ctypes.POINTER(SoundIoDevice))
        LOGGER.info('Input Device: %s' % pydevice.contents.name.decode())
        self.sort_channel_layouts(self.input_device)

        if self.sample_rate:
            if not self.supports_sample_rate(self.input_device, self.sample_rate):
                raise PySoundIoError('Invalid sample rate: %d' % self.sample_rate)
        else:
            self.sample_rate = self.get_default_sample_rate(self.input_device)

        if self.format:
            if not self.supports_format(self.input_device, self.format):
                raise PySoundIoError('Invalid format: %s interleaved' %
                                     (soundio.format_string(self.format)))
        else:
            self.format = self.get_default_format(self.input_device)

        self._create_input_stream()
        self._open_input_stream()
        pystream = _ctypes.cast(self.input_stream, _ctypes.POINTER(SoundIoInStream))
        self.input_bytes_per_frame = pystream.contents.bytes_per_frame
        capacity = (DEFAULT_RING_BUFFER_DURATION *
                    pystream.contents.sample_rate * pystream.contents.bytes_per_frame)
        self._create_input_ring_buffer(capacity)
        self._start_input_stream()
        self.flush()

    def _create_output_stream(self):
        """
        Allocates memory and sets defaults for output stream
        """
        self.output_stream = soundio.outstream_create(self.output_device)
        if not self.output_stream:
            raise PySoundIoError('Could not create output stream')

        pystream = _ctypes.cast(self.output_stream, _ctypes.POINTER(SoundIoOutStream))
        if not self.testing:
            soundio.set_write_callback(self._write_callback)

        layout = self._get_default_layout(self.channels)
        pylayout = _ctypes.cast(layout, _ctypes.POINTER(SoundIoChannelLayout))
        pystream.contents.layout = pylayout.contents

        pystream.contents.format = self.format
        pystream.contents.sample_rate = self.sample_rate
        if self.block_size:
            pystream.contents.software_latency = float(self.block_size) / self.sample_rate

        return self.output_stream

    def _open_output_stream(self):
        """
        Open an output stream.
        """
        soundio.outstream_open()
        pystream = _ctypes.cast(self.output_stream, _ctypes.POINTER(SoundIoOutStream))
        self.block_size = int(pystream.contents.software_latency / self.sample_rate)

    def _start_output_stream(self):
        """
        Start an output stream running.
        """
        soundio.outstream_start()

    def pause_output_stream(self, pause):
        """
        Pause output stream

        Parameters
        ----------
        pause: (bool) True to pause, False to unpause
        """
        soundio.outstream_pause(pause)

    def _write_callback(self, size):
        """
        Internal write callback.
        """
        _OutputProcessingThread(parent=self, block_size=size).start()

    def _underflow_callback(self, stream):
        """
        Internal underflow callback, which calls the external
        underflow callback if defined.
        """
        if self.underflow_callback:
            self.underflow_callback(stream)

    def _clear_output_buffer(self):
        """
        Clear the output buffer
        """
        if self.output_buffer:
            soundio.ring_buffer_clear(self.output_buffer)

    def get_output_latency(self, out_latency):
        """
        Obtain the total number of seconds that the next frame written
        will take to become audible.

        Parameters
        ----------
        out_latency: (int) output latency in seconds
        """
        return soundio.outstream_get_latency(out_latency)

    def start_output_stream(self, device_id=None,
                            sample_rate=None, dtype=None,
                            block_size=None, channels=None,
                            write_callback=None):
        """
        Creates output stream, and sets parameters. Then allocates
        a ring buffer and starts the stream.

        The write callback is called in an audio processing thread,
        when a block of data should be passed to the speakers. Data is
        added to the ring buffer to process.

        Parameters
        ----------
        device_id: (int) output device id
        sample_rate: (int) desired sample rate (optional)
        dtype: (SoundIoFormat) desired format, see `Formats`_. (optional)
        block_size: (int) desired block size (optional)
        channels: (int) number of channels [1: mono, 2: stereo] (optional)
        write_callback: (fn) function to call with data, the function must have
                        the arguments data and length.

        Raises
        ------
        PySoundIoError if any invalid parameters are used

        Notes
        -----
        An example write callback

        .. code-block:: python
            :linenos:

            def write_callback(data, length):
                outdata = ar.array('f', [0] * length)
                for value in outdata:
                    outdata = 1.0
                data[:] = outdata.tostring()
        """
        self.sample_rate = sample_rate
        self.format = dtype
        self.block_size = block_size
        self.channels = channels
        self.write_callback = write_callback

        if device_id:
            self.output_device = self.get_output_device(device_id)
        else:
            self.output_device = self.get_default_output_device()

        pydevice = _ctypes.cast(self.output_device, _ctypes.POINTER(SoundIoDevice))
        LOGGER.info('Input Device: %s' % pydevice.contents.name.decode())
        self.sort_channel_layouts(self.output_device)

        if self.sample_rate:
            if not self.supports_sample_rate(self.output_device, self.sample_rate):
                raise PySoundIoError('Invalid sample rate: %d' % self.sample_rate)
        else:
            self.sample_rate = self.get_default_sample_rate(self.output_device)

        if self.format:
            if not self.supports_format(self.output_device, self.format):
                raise PySoundIoError('Invalid format: %s interleaved' %
                                     (soundio.format_string(self.format)))
        else:
            self.format = self.get_default_format(self.output_device)

        self._create_output_stream()
        self._open_output_stream()
        pystream = _ctypes.cast(self.output_stream, _ctypes.POINTER(SoundIoOutStream))
        self.output_bytes_per_frame = pystream.contents.bytes_per_frame
        capacity = (DEFAULT_RING_BUFFER_DURATION *
                    pystream.contents.sample_rate * pystream.contents.bytes_per_frame)
        self._create_output_ring_buffer(capacity)
        self._clear_output_buffer()

        length = self.block_size if self.block_size else 4096
        data = bytearray(b'\x00' * length * self.output_bytes_per_frame)
        soundio.ring_buffer_write_ptr(self.output_buffer, data, len(data))
        soundio.ring_buffer_advance_write_ptr(self.output_buffer, len(data))

        self._start_output_stream()
        self.flush()
