"""
Detection strategy factory.

Equivalent to Laravel Boost's DetectionStrategyFactory.
"""

from .detection_strategy import (
    CommandDetectionStrategy,
    CompositeDetectionStrategy,
    DetectionStrategy,
    DirectoryDetectionStrategy,
    FileDetectionStrategy,
)


class DetectionStrategyFactory:
    """Creates the appropriate detection strategy from config."""

    def make_from_config(self, config: dict) -> DetectionStrategy:
        """Auto-detect strategy type from config keys."""
        strategies = []

        if "command" in config:
            strategies.append(CommandDetectionStrategy())
        if "files" in config:
            strategies.append(FileDetectionStrategy())
        if "paths" in config:
            strategies.append(DirectoryDetectionStrategy())

        if len(strategies) > 1:
            return CompositeDetectionStrategy(strategies)
        elif len(strategies) == 1:
            return strategies[0]

        # Fallback
        return CompositeDetectionStrategy(strategies)
