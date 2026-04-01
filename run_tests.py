"""Run all PatientMA tests."""
import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "shared/test_shared.py",
         "shared/test_classifier.py",
         "shared/test_stats.py",
         "shared/test_intervention.py",
         "shared/test_composite.py",
         "OutcomeGap/test_gaps.py",
         "OutcomeGap/test_og_angles.py",
         "TrialFit/test_fit.py",
         "TrialFit/test_tf_angles.py",
         "Transparency/test_transparency.py",
         "Transparency/test_geographic.py",
         "Evolution/test_evolution.py",
         "Evidence/test_evidence.py",
         "-v", "--tb=short"],
        cwd=root,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
