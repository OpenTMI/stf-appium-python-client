import unittest
import time
import signal
import weakref
from stf_appium_client.tools import find_free_port, GracefulProcess


def try_until(func, max_tries, sleep_time):
    for _ in range(0,max_tries):
        try:
            return func()
        except:
            time.sleep(sleep_time)
    raise AssertionError('timeout')


class TestTools(unittest.TestCase):

    #def setUp(self):
    #    self._default_handler = signal.getsignal(signal.SIGINT)

    #def tearDown(self):
    #    signal.signal(signal.SIGINT, self._default_handler)
    #    unittest.signals._results = weakref.WeakKeyDictionary()
    #    unittest.signals._interrupt_handler = None

    def test_port(self):
        for i in range(10):
            port = find_free_port()
            self.assertTrue(isinstance(port, int))

    def test_graceful_process_sigint(self):
        process = GracefulProcess('sleep 10')
        self.assertTrue(process._exists())

        # Simulate sigint signal from head process
        process._sigint(None, None)

        def test():
            assert not process._exists()

        exists = try_until(test, 100, 0.01)
        self.assertFalse(exists)
        self.assertTrue(process._checkpoint())
        process.communicate()
        self.assertEqual(process.returncode, -2)
