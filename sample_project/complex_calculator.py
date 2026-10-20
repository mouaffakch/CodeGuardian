def calculate_insurance_premium(age, driving_years, accidents, violations, vehicle_type, coverage_level):
    """
    DEFECT: Excessively high cyclomatic & cognitive complexity (COMPLEXITY001)
    and too many parameters (SMELL005)
    """
    base_rate = 500.0

    if age < 18:
        return 0.0
    elif age < 25:
        base_rate += 300.0
        if driving_years < 2:
            base_rate += 150.0
            if vehicle_type == "SPORTS":
                base_rate += 400.0
            elif vehicle_type == "SUV":
                base_rate += 100.0
    elif age < 65:
        base_rate += 50.0
        if driving_years > 10:
            base_rate -= 50.0
            if vehicle_type == "SEDAN":
                base_rate -= 30.0
    else:
        base_rate += 120.0

    if accidents > 0:
        if accidents == 1:
            base_rate *= 1.25
        elif accidents == 2:
            base_rate *= 1.6
        else:
            base_rate *= 2.2
            if violations > 2:
                base_rate += 500.0

    if violations > 0:
        if violations == 1:
            base_rate += 80.0
        elif violations == 2:
            base_rate += 180.0
        else:
            base_rate += 350.0

    if coverage_level == "PREMIUM":
        base_rate *= 1.5
    elif coverage_level == "COMPREHENSIVE":
        base_rate *= 1.3
    elif coverage_level == "BASIC":
        base_rate *= 1.0
    else:
        base_rate *= 0.9

    return round(base_rate, 2)
