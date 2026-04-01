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
         "OutcomeGap/test_gaps.py",
         "TrialFit/test_fit.py",
         "Evidence/test_evidence.py",
         "-v", "--tb=short"],
        cwd=root,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
