from cli.app import PolychromeCLIApp


# @pytest.mark.asyncio
def test_login(snap_compare):
    """Test pressing keys has the desired result."""
    app = PolychromeCLIApp()
    assert snap_compare(app)

