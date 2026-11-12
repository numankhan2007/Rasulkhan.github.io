"""
Standard unittest wrapper for discoverability.
Runs the 4-tier E2E portfolio test suite.
"""

from tests.verify_portfolio import (
    TestTier1FeatureCoverage,
    TestTier2BoundaryEdgeSyntax,
    TestTier3CrossFeatureLoadingAnimation,
    TestTier4RealWorldLocalServer,
)

__all__ = [
    "TestTier1FeatureCoverage",
    "TestTier2BoundaryEdgeSyntax",
    "TestTier3CrossFeatureLoadingAnimation",
    "TestTier4RealWorldLocalServer",
]

if __name__ == "__main__":
    import unittest
    unittest.main()
