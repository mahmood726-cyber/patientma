"""Pure-math statistical utilities — NO external dependencies (no scipy, no numpy).

Functions:
    normal_cdf, normal_ppf_approx, chi_squared_cdf_approx,
    chi_squared_2x2, cramers_v, mann_whitney_u, rank_biserial,
    segmented_regression, logistic_regression_simple
"""

import math

# ---------------------------------------------------------------------------
# Normal distribution
# ---------------------------------------------------------------------------


def normal_cdf(x):
    """Cumulative distribution function of the standard normal via math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_ppf_approx(p):
    """Rational approximation of the inverse standard normal (Abramowitz & Stegun 26.2.23).

    Accurate to ~4.5e-4 for 0 < p < 1.
    """
    if p <= 0 or p >= 1:
        raise ValueError("p must be in (0, 1)")
    if p < 0.5:
        return -normal_ppf_approx(1.0 - p)
    t = math.sqrt(-2.0 * math.log(1.0 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1.0 + d1 * t + d2 * t * t + d3 * t * t * t)


# ---------------------------------------------------------------------------
# Chi-squared distribution
# ---------------------------------------------------------------------------


def chi_squared_cdf_approx(chi2, df):
    """Approximate CDF of the chi-squared distribution using the Wilson-Hilferty transform.

    Formula: chi2 ~ df * (1 - 2/(9*df) + z*sqrt(2/(9*df)))^3
    We invert this to get z, then use normal_cdf.
    """
    if df <= 0:
        raise ValueError("df must be positive")
    if chi2 <= 0:
        return 0.0
    # Wilson-Hilferty cube-root transform
    k = df
    z = ((chi2 / k) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * k))) / math.sqrt(
        2.0 / (9.0 * k)
    )
    return normal_cdf(z)


# ---------------------------------------------------------------------------
# 2x2 contingency table
# ---------------------------------------------------------------------------


def chi_squared_2x2(a, b, c, d):
    """Chi-squared test for a 2x2 table with Yates continuity correction.

    Layout:   | col1 | col2
    --------- |------|-----
    row1      |  a   |  b
    row2      |  c   |  d

    Returns (chi2, p_value).
    """
    n = a + b + c + d
    if n == 0:
        return (0.0, 1.0)
    # Yates correction
    numerator = abs(a * d - b * c) - n / 2.0
    if numerator < 0:
        numerator = 0.0
    chi2 = (n * numerator * numerator) / (
        (a + b) * (c + d) * (a + c) * (b + d)
    )
    p_value = 1.0 - chi_squared_cdf_approx(chi2, 1)
    return (chi2, p_value)


def cramers_v(a, b, c, d):
    """Cramer's V for a 2x2 table (equals |phi| for 2x2)."""
    n = a + b + c + d
    if n == 0:
        return 0.0
    # No Yates correction for Cramer's V — use standard phi coefficient
    numerator = a * d - b * c
    denominator = (a + b) * (c + d) * (a + c) * (b + d)
    if denominator == 0:
        return 0.0
    phi_sq = (numerator * numerator) / denominator
    # For 2x2, phi^2 = (ad-bc)^2 / ((a+b)(c+d)(a+c)(b+d))
    # Cramer's V = sqrt(phi^2 / (n * min(r-1, c-1))) = sqrt(phi^2 / n) for 2x2
    # But phi^2 here is NOT chi2/n — it's the raw cross-product ratio.
    # chi2 = n * phi_sq, so V = sqrt(chi2 / (n * min(r-1,c-1))) = sqrt(phi_sq) for 2x2
    return math.sqrt(phi_sq)


# ---------------------------------------------------------------------------
# Mann-Whitney U
# ---------------------------------------------------------------------------


def _rank_data(combined):
    """Assign ranks with tied-rank averaging. Returns list of ranks in original order."""
    n = len(combined)
    indexed = sorted(range(n), key=lambda i: combined[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and combined[indexed[j]] == combined[indexed[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0  # 1-based average
        for k in range(i, j):
            ranks[indexed[k]] = avg_rank
        i = j
    return ranks


def mann_whitney_u(group1, group2):
    """Mann-Whitney U test with normal approximation (including tie correction).

    Returns (U, p_value) — two-sided.
    """
    n1 = len(group1)
    n2 = len(group2)
    if n1 == 0 or n2 == 0:
        return (0.0, 1.0)

    combined = list(group1) + list(group2)
    ranks = _rank_data(combined)

    r1 = sum(ranks[:n1])
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u_stat = min(u1, u2)

    # Normal approximation
    mu = n1 * n2 / 2.0
    n = n1 + n2

    # Tie correction
    # Count groups of ties
    sorted_vals = sorted(combined)
    tie_sum = 0.0
    i = 0
    while i < n:
        j = i
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        t = j - i
        if t > 1:
            tie_sum += t * t * t - t
        i = j

    sigma = math.sqrt(
        n1 * n2 / 12.0 * ((n + 1) - tie_sum / (n * (n - 1)))
    )

    if sigma == 0:
        return (u_stat, 1.0)

    z = (u_stat - mu) / sigma
    # Two-sided p-value
    p_value = 2.0 * normal_cdf(z)  # z is always <= 0 since u_stat = min(u1,u2)
    return (u_stat, p_value)


def rank_biserial(group1, group2):
    """Rank-biserial correlation: r = 2*U1/(n1*n2) - 1.

    Positive when group1 > group2 on average, negative when group1 < group2.
    U1 counts how often group1 values exceed group2 values.
    Returns value in [-1, 1].
    """
    n1 = len(group1)
    n2 = len(group2)
    if n1 == 0 or n2 == 0:
        return 0.0

    combined = list(group1) + list(group2)
    ranks = _rank_data(combined)
    r1 = sum(ranks[:n1])
    u1 = r1 - n1 * (n1 + 1) / 2.0
    return (2.0 * u1) / (n1 * n2) - 1.0


# ---------------------------------------------------------------------------
# OLS helper
# ---------------------------------------------------------------------------


def _ols_fit(x, y):
    """Ordinary least squares: y = a + b*x.

    Returns (a, b, residuals, sse).
    """
    n = len(x)
    sx = sum(x)
    sy = sum(y)
    sxx = sum(xi * xi for xi in x)
    sxy = sum(xi * yi for xi, yi in zip(x, y))

    denom = n * sxx - sx * sx
    if abs(denom) < 1e-15:
        a = sy / n if n > 0 else 0.0
        b = 0.0
    else:
        b = (n * sxy - sx * sy) / denom
        a = (sy - b * sx) / n

    residuals = [yi - (a + b * xi) for xi, yi in zip(x, y)]
    sse = sum(r * r for r in residuals)
    return (a, b, residuals, sse)


# ---------------------------------------------------------------------------
# Segmented regression
# ---------------------------------------------------------------------------


def segmented_regression(x, y, max_breakpoints=3):
    """Fit piecewise-linear models with 0..max_breakpoints breakpoints.

    Uses BIC for model selection among candidate breakpoints placed at data x-values.
    Returns dict: {n_breakpoints, breakpoints, segments, bic}.
    """
    n = len(x)
    if n < 4:
        a, b, _, sse = _ols_fit(x, y)
        return {
            "n_breakpoints": 0,
            "breakpoints": [],
            "segments": [{"start": min(x), "end": max(x), "slope": b, "intercept": a}],
            "bic": _bic(sse, n, 2),
        }

    # Sort by x
    order = sorted(range(n), key=lambda i: x[i])
    xs = [x[i] for i in order]
    ys = [y[i] for i in order]

    # 0 breakpoints (simple linear)
    a0, b0, _, sse0 = _ols_fit(xs, ys)
    best_bic = _bic(sse0, n, 2)
    best_result = {
        "n_breakpoints": 0,
        "breakpoints": [],
        "segments": [{"start": xs[0], "end": xs[-1], "slope": b0, "intercept": a0}],
        "bic": best_bic,
    }

    # Try 1..max_breakpoints
    # Candidate breakpoints: interior x-values (skip first 2 and last 2 for enough data)
    candidates = xs[2:-2] if n > 4 else []
    # Remove duplicates and sort
    candidates = sorted(set(candidates))

    for nb in range(1, max_breakpoints + 1):
        if len(candidates) < nb:
            break
        # For nb=1, try each candidate; for nb>1, try combinations (greedy for efficiency)
        if nb == 1:
            for bp in candidates:
                result = _fit_with_breakpoints(xs, ys, [bp])
                if result["bic"] < best_bic:
                    best_bic = result["bic"]
                    best_result = result
        else:
            # Greedy: start from best single breakpoint, add one at a time
            current_bps = list(best_result["breakpoints"][:nb - 1]) if best_result["n_breakpoints"] >= nb - 1 else []
            best_add_bic = float("inf")
            best_add_bp = None
            for bp in candidates:
                if bp in current_bps:
                    continue
                trial_bps = sorted(current_bps + [bp])
                result = _fit_with_breakpoints(xs, ys, trial_bps)
                if result["bic"] < best_add_bic:
                    best_add_bic = result["bic"]
                    best_add_bp = bp
            if best_add_bp is not None:
                trial_bps = sorted(current_bps + [best_add_bp])
                result = _fit_with_breakpoints(xs, ys, trial_bps)
                if result["bic"] < best_bic:
                    best_bic = result["bic"]
                    best_result = result

    return best_result


def _fit_with_breakpoints(xs, ys, breakpoints):
    """Fit piecewise-linear model with given breakpoints. Returns result dict."""
    n = len(xs)
    bps = sorted(breakpoints)
    edges = [xs[0]] + bps + [xs[-1]]
    segments = []
    total_sse = 0.0

    for seg_i in range(len(edges) - 1):
        lo, hi = edges[seg_i], edges[seg_i + 1]
        # Include points in [lo, hi] for first/last segment; for internal, (lo, hi]
        seg_x = []
        seg_y = []
        for i in range(n):
            if seg_i == 0:
                if xs[i] <= hi:
                    seg_x.append(xs[i])
                    seg_y.append(ys[i])
            elif seg_i == len(edges) - 2:
                if xs[i] > lo:
                    seg_x.append(xs[i])
                    seg_y.append(ys[i])
            else:
                if lo < xs[i] <= hi:
                    seg_x.append(xs[i])
                    seg_y.append(ys[i])

        if len(seg_x) < 2:
            # Not enough points for this segment; fall back
            seg_x_all = list(xs)
            seg_y_all = list(ys)
            a, b, _, sse = _ols_fit(seg_x_all, seg_y_all)
        else:
            a, b, _, sse = _ols_fit(seg_x, seg_y)
        total_sse += sse
        segments.append({"start": lo, "end": hi, "slope": b, "intercept": a})

    # Parameters: 2 per segment (slope + intercept)
    k = 2 * len(segments)
    bic = _bic(total_sse, n, k)

    return {
        "n_breakpoints": len(bps),
        "breakpoints": bps,
        "segments": segments,
        "bic": bic,
    }


def _bic(sse, n, k):
    """Bayesian Information Criterion: n*log(sse/n) + k*log(n)."""
    if n <= 0 or sse <= 0:
        return float("inf")
    return n * math.log(sse / n) + k * math.log(n)


# ---------------------------------------------------------------------------
# Logistic regression (simple gradient descent)
# ---------------------------------------------------------------------------


def logistic_regression_simple(X, y, max_iter=50):
    """Simple logistic regression via gradient descent.

    X: list of lists (n_samples x n_features)
    y: list of 0/1 labels
    max_iter: maximum iterations
    learning_rate: fixed at 0.1

    Returns dict: {intercept, coefficients, iterations}.
    """
    n = len(y)
    if n == 0:
        return {"intercept": 0.0, "coefficients": [], "iterations": 0}

    p = len(X[0]) if X else 0

    # Initialize weights: intercept + p coefficients
    w = [0.0] * (p + 1)
    lr = 0.1

    for iteration in range(1, max_iter + 1):
        # Compute gradients
        grad = [0.0] * (p + 1)
        for i in range(n):
            # Linear combination: w[0] + w[1]*x1 + w[2]*x2 + ...
            z = w[0]
            for j in range(p):
                z += w[j + 1] * X[i][j]
            # Sigmoid
            prob = _sigmoid(z)
            err = prob - y[i]
            grad[0] += err
            for j in range(p):
                grad[j + 1] += err * X[i][j]

        # Update
        for j in range(p + 1):
            w[j] -= lr * grad[j] / n

    return {
        "intercept": w[0],
        "coefficients": w[1:],
        "iterations": max_iter,
    }


def _sigmoid(z):
    """Numerically stable sigmoid function."""
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    else:
        ez = math.exp(z)
        return ez / (1.0 + ez)
