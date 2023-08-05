from .context import *

import unittest
from benchit import BenchIt


class BenchItSuite(unittest.TestCase):

    def test_benchit(self):
        """
        Full benchmark test.
        Test starting, marking, stopping, and displaying the benchmark.
        """
        b = BenchIt()

        # Ensure start key is set on init
        self.assertEqual(len(b.times), 1)
        self.assertIn('_start', b.times.keys())

        # Set a marker
        "code marker"; b()
        "more code"; b("__call__ marker")
        b.mark('Unique Marker')
        self.assertIn('"code marker"', b.times.keys())
        self.assertIn('__call__ marker', b.times.keys())
        self.assertIn('Unique Marker', b.times.keys())

        # Stop the benchmark
        b.stop()
        self.assertIn('_end', b.times.keys())

        # Ensure end time is after the start time
        self.assertGreater(b.times['_end'], b.times['_start'])

        # Check the output table
        with capture(b.display) as output:
            self.assertIn("Avg Time", output)
            self.assertIn("Unique Marker", output)
            self.assertIn("Total runtime", output)
            self.assertIn("test_benchit", output)

    def test_singleton(self):
        """Test to ensure mutiple calls to benchit return the same object
        """
        b = BenchIt()
        b2 = BenchIt()
        self.assertEqual(b, b2)
        self.assertEqual(b.timer_name, "BenchIt")

        b3 = BenchIt("New Bencher")
        self.assertNotEqual(b, b3)
        self.assertEqual(b3.timer_name, "New Bencher")

        b4 = BenchIt(timer_name="New Bencher")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BenchItSuite))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
