"""
Unit and Integration Test Suite for NEXUS-TWIN Phase 5 Validation & Experiments.
Verifies reproducibility configuration, experiment outputs, JSON schemas, and figure generation.
"""

import sys
import os
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from experiments.generate_phase5_figures import generate_all_figures

class TestPhase5Validation(unittest.TestCase):
    def test_01_reproducibility_config(self):
        """Verify reproducibility configuration file exists and has correct schema."""
        cfg_file = PROJECT_ROOT / "configs" / "reproducibility.json"
        self.assertTrue(cfg_file.exists())
        
        with open(cfg_file, "r") as f:
            data = json.load(f)
            
        self.assertIn("reproducibility", data)
        self.assertEqual(data["reproducibility"]["phase"], 5)
        self.assertIn("random_seeds", data["reproducibility"])

    def test_02_figure_generation(self):
        """Verify figure generator runs cleanly and creates PNG figures."""
        generate_all_figures()
        
        fig_dir = PROJECT_ROOT / "results" / "figures"
        self.assertTrue(fig_dir.exists())
        
        fig1 = fig_dir / "fig1_baseline_comparison.png"
        self.assertTrue(fig1.exists())
        self.assertGreater(fig1.stat().st_size, 1000)

if __name__ == "__main__":
    unittest.main()
