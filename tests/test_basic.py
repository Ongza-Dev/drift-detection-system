"""
Basic tests to verify setup is working
"""

from drift_detection import __version__


def test_version():
    """Test that version is defined"""
    assert __version__ == "0.1.0"


def test_import():
    """Test that package can be imported"""
    import drift_detection

    assert drift_detection is not None


class TestBasicFunctionality:
    """Basic functionality tests"""

    def test_placeholder(self):
        """Placeholder test - replace with real tests later"""
        assert True

    def test_math_works(self):
        """Verify Python math works (sanity check)"""
        assert 2 + 2 == 4
        assert 10 / 2 == 5
