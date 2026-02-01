def enforce_kpi(score: float):
    threshold = 0.9899
    if score >= threshold:
        return "PASS"
    elif score >= 0.97:
        return "IMPROVE"
    else:
        return "FAIL"
