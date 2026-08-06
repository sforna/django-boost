"""
Tests for platform detection and agent detection strategies.
"""

from django_boost.install.detection.detection_strategy import (
    CommandDetectionStrategy,
    DirectoryDetectionStrategy,
    FileDetectionStrategy,
)
from django_boost.install.detection.factory import DetectionStrategyFactory
from django_boost.install.enums.platform import Platform


class TestPlatform:
    """Tests for Platform enum."""

    def test_current_is_valid(self):
        """Current platform should be a valid Platform member."""
        current = Platform.current()
        assert isinstance(current, Platform)
        assert current in (Platform.DARWIN, Platform.LINUX, Platform.WINDOWS, Platform.UNKNOWN)

    def test_from_string(self):
        """Should map system strings correctly."""
        assert Platform("darwin") == Platform.DARWIN
        assert Platform("linux") == Platform.LINUX
        assert Platform("windows") == Platform.WINDOWS


class TestFileDetection:
    """Tests for FileDetectionStrategy."""

    def test_detects_existing_file(self, tmp_path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("hello")

        strategy = FileDetectionStrategy()
        config = {"files": ["test.txt"], "basePath": str(tmp_path)}
        assert strategy.detect(config) is True

    def test_does_not_detect_missing_file(self, tmp_path):
        strategy = FileDetectionStrategy()
        config = {"files": ["nonexistent.txt"], "basePath": str(tmp_path)}
        assert strategy.detect(config) is False


class TestDirectoryDetection:
    """Tests for DirectoryDetectionStrategy."""

    def test_detects_existing_dir(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        strategy = DirectoryDetectionStrategy()
        config = {"paths": ["subdir"], "basePath": str(tmp_path)}
        assert strategy.detect(config) is True

    def test_does_not_detect_missing_dir(self, tmp_path):
        strategy = DirectoryDetectionStrategy()
        config = {"paths": ["nonexistent"], "basePath": str(tmp_path)}
        assert strategy.detect(config) is False


class TestDetectionFactory:
    """Tests for DetectionStrategyFactory."""

    def test_creates_command_strategy(self):
        factory = DetectionStrategyFactory()
        strategy = factory.make_from_config({"command": "echo hi"})
        assert isinstance(strategy, CommandDetectionStrategy)

    def test_creates_file_strategy(self):
        factory = DetectionStrategyFactory()
        strategy = factory.make_from_config({"files": ["test.txt"]})
        assert isinstance(strategy, FileDetectionStrategy)

    def test_creates_directory_strategy(self):
        factory = DetectionStrategyFactory()
        strategy = factory.make_from_config({"paths": ["src"]})
        assert isinstance(strategy, DirectoryDetectionStrategy)

    def test_creates_composite_for_multiple_keys(self):
        factory = DetectionStrategyFactory()
        strategy = factory.make_from_config(
            {
                "command": "which pi",
                "paths": [".pi"],
            }
        )
        # Should be composite when multiple detection methods exist
        from django_boost.install.detection.detection_strategy import (
            CompositeDetectionStrategy,
        )

        assert isinstance(strategy, CompositeDetectionStrategy)
