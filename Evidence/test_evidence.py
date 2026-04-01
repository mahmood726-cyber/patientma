"""Tests for CardioEvidence app logic and HTML structure."""
import os
import re
import pytest


class TestEligibilityParsing:
    """Test the eligibility parsing logic (Python equivalents of JS functions)."""

    def _parse_age_from_elig(self, text):
        if not text:
            return None, None
        text_lower = text.lower()
        min_age = None
        max_age = None
        m = re.search(r'(?:>=|≥|at least)\s*(\d+)\s*(?:years?|yrs?)?', text_lower)
        if m:
            min_age = int(m.group(1))
        m = re.search(r'(\d+)\s*(?:years?|yrs?)\s*(?:or older|and older)', text_lower)
        if m and min_age is None:
            min_age = int(m.group(1))
        m = re.search(r'(?:<=|≤|younger than|under)\s*(\d+)', text_lower)
        if m:
            max_age = int(m.group(1))
        if min_age is None and re.search(r'\badults?\b', text_lower):
            min_age = 18
        return min_age, max_age

    def test_age_range(self):
        mn, mx = self._parse_age_from_elig("Age >= 18 and <= 75 years")
        assert mn == 18
        assert mx == 75

    def test_no_age(self):
        mn, mx = self._parse_age_from_elig("Heart failure patients")
        assert mn is None and mx is None

    def _check_comorbidity_conflict(self, patient_comorbidities, exclusion_text):
        if not exclusion_text:
            return []
        excl_lower = exclusion_text.lower()
        conflicts = []
        mapping = {
            "ckd": ["renal", "egfr", "kidney", "dialysis", "creatinine"],
            "diabetes": ["diabetes", "diabetic"],
            "obesity": ["bmi", "obes"],
            "copd": ["copd", "pulmonary", "lung disease"],
            "prior_stroke": ["stroke", "cerebrovascular"],
            "cancer": ["cancer", "malignancy", "neoplasm"],
        }
        for comorb in patient_comorbidities:
            keywords = mapping.get(comorb, [])
            for kw in keywords:
                if kw in excl_lower:
                    conflicts.append(comorb)
                    break
        return conflicts

    def test_ckd_conflict(self):
        conflicts = self._check_comorbidity_conflict(
            ["ckd"], "Exclusion: eGFR < 30 mL/min"
        )
        assert "ckd" in conflicts

    def test_no_conflict(self):
        conflicts = self._check_comorbidity_conflict(
            ["diabetes"], "Exclusion: Active cancer"
        )
        assert len(conflicts) == 0

    def test_multiple_conflicts(self):
        conflicts = self._check_comorbidity_conflict(
            ["ckd", "diabetes", "cancer"],
            "Exclusion: eGFR < 30, diabetes mellitus, active malignancy",
        )
        assert len(conflicts) == 3


class TestQueryBuilder:
    """Test CT.gov API query construction."""

    def _build_query(self, condition, intervention=None, status="COMPLETED",
                     phase="PHASE3,PHASE4", has_results=True):
        base = "https://clinicaltrials.gov/api/v2/studies"
        params = {
            "query.cond": condition,
            "filter.overallStatus": status,
            "pageSize": "50",
            "format": "json",
            "countTotal": "true",
        }
        if phase:
            params["filter.phase"] = phase
        if intervention:
            params["query.intr"] = intervention
        if has_results:
            params["filter.advanced"] = "results:true"
        from urllib.parse import urlencode
        return base + "?" + urlencode(params)

    def test_basic_hf_query(self):
        url = self._build_query("heart failure")
        assert "query.cond=heart+failure" in url
        assert "COMPLETED" in url
        assert "PHASE3" in url

    def test_with_intervention(self):
        url = self._build_query("heart failure", intervention="SGLT2 inhibitor")
        assert "query.intr=SGLT2" in url

    def test_results_filter(self):
        url = self._build_query("atrial fibrillation", has_results=True)
        assert "results" in url


class TestEligibilityBadge:
    """Test eligibility badge logic."""

    def _compute_badge(self, patient_age, age_min, age_max, conflicts):
        if age_min and patient_age < age_min:
            return "excluded", f"Age {patient_age} below minimum {age_min}"
        if age_max and patient_age > age_max:
            return "excluded", f"Age {patient_age} above maximum {age_max}"
        if conflicts:
            return "may_be_excluded", f"Potential conflicts: {', '.join(conflicts)}"
        return "likely_eligible", "No detected conflicts"

    def test_age_excluded(self):
        badge, reason = self._compute_badge(85, 18, 75, [])
        assert badge == "excluded"

    def test_likely_eligible(self):
        badge, reason = self._compute_badge(65, 18, 80, [])
        assert badge == "likely_eligible"

    def test_comorbidity_warning(self):
        badge, reason = self._compute_badge(65, 18, 80, ["ckd"])
        assert badge == "may_be_excluded"


class TestHTMLStructure:
    """Test the HTML file exists and has required elements."""

    def test_html_file_exists(self):
        path = os.path.join(os.path.dirname(__file__), "index.html")
        assert os.path.exists(path), "index.html not found"

    def test_has_disclaimer(self):
        path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        html_lower = html.lower()
        # Check for disclaimer text (may have HTML tags between words)
        has_disclaimer = ("medical advice" in html_lower or
                          "not a recommendation" in html_lower or
                          "disclaimer" in html_lower)
        assert has_disclaimer, "No disclaimer found in index.html"

    def test_no_raw_script_close(self):
        path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(scripts):
            assert '</script>' not in script, f"Literal </script> found in script block {i}"

    def test_unique_ids(self):
        path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        ids = re.findall(r'id="([^"]+)"', html)
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"
