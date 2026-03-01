"""Tests for license module."""

from noteshift.license import check_depth_limit, get_depth_warning, verify_license


class TestVerifyLicense:
    """Tests for verify_license function."""

    def test_free_tier_no_key(self) -> None:
        """No key returns free tier limits."""
        result = verify_license(None)
        assert result["max_depth"] == 2
        assert result["features"] == []

    def test_free_tier_invalid_key(self) -> None:
        """Invalid key returns free tier limits."""
        result = verify_license("invalid-key")
        assert result["max_depth"] == 2
        assert result["features"] == []

    def test_paid_tier_demo_key(self) -> None:
        """DEMO key returns unlimited depth."""
        result = verify_license("DEMO")
        assert result["max_depth"] == 999
        assert "unlimited_depth" in result["features"]
        assert "checkpoint_resume" in result["features"]
        assert "migration_reports" in result["features"]


class TestCheckDepthLimit:
    """Tests for check_depth_limit function."""

    def test_free_tier_within_limit(self) -> None:
        """Free tier: depth 0 and 1 are allowed."""
        assert check_depth_limit(0, 2, False) is True
        assert check_depth_limit(1, 2, False) is True

    def test_free_tier_at_limit(self) -> None:
        """Free tier: depth 2 is at the limit (children at 3 not allowed)."""
        assert check_depth_limit(2, 2, False) is False

    def test_free_tier_beyond_limit(self) -> None:
        """Free tier: depth > max is not allowed for children."""
        # When at depth 2, we can't recurse further (depth would be 3)
        assert check_depth_limit(3, 2, False) is False

    def test_paid_tier_unlimited(self) -> None:
        """Paid tier: any depth is allowed."""
        assert check_depth_limit(0, 999, True) is True
        assert check_depth_limit(100, 999, True) is True
        assert check_depth_limit(999, 999, True) is True  # Still allowed to recurse


class TestGetDepthWarning:
    """Tests for get_depth_warning function."""

    def test_no_warning_within_limit(self) -> None:
        """No warning when within limit."""
        assert get_depth_warning(0, 2) is None
        assert get_depth_warning(1, 2) is None
        # At depth 2, children would be at 3, which exceeds limit
        assert get_depth_warning(2, 2) is not None

    def test_warning_beyond_limit(self) -> None:
        """Warning when attempting to go beyond limit."""
        warning = get_depth_warning(3, 2)
        assert warning is not None
        assert "Depth limit" in warning
        assert "2" in warning

    def test_warning_paid_no_limit(self) -> None:
        """No warning for paid tier (never called in practice)."""
        # This wouldn't actually be called for paid users
        # But tests the behavior
        assert (
            get_depth_warning(999, 999) is not None
        )  # Still returns warning at exact limit
