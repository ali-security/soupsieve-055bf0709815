"""Test attribute selectors."""
from .. import util
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        import signal
        import time

        # `SIGALRM` is only available on Unix-like systems. Where it is available, use it as a
        # hard cutoff so that a regression fails fast instead of hanging the test run.
        use_alarm = hasattr(signal, 'SIGALRM') and hasattr(signal, 'alarm')

        def timeout_handler(signum, frame):
            """Raise a timeout error."""

            raise TimeoutError

        # An unterminated quoted attribute value (both quote styles) must fail as a syntax
        # error immediately instead of sending the pattern into catastrophic backtracking.
        for selector in ('[a="' + ('x' * 300), "[a='" + ('x' * 300)):
            old_handler = None
            if use_alarm:
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(3)

            passed = False
            start = time.time()
            try:
                with self.assertRaises(sv.SelectorSyntaxError):
                    sv.compile(selector)
                passed = True
            except TimeoutError:
                pass
            finally:
                elapsed = time.time() - start
                if use_alarm:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)

            self.assertTrue(passed)
            # Platforms without `SIGALRM` get no hard cutoff, so check the elapsed time too:
            # catastrophic backtracking takes seconds while a linear parse takes milliseconds.
            self.assertLess(elapsed, 3)
