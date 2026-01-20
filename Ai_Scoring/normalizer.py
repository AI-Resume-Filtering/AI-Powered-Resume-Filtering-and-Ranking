
# scoring_engine/normalizer.py

def normalize(value: int | float, cap: int | float) -> float:
    """
    Converts a value into a range between 0 and 1 using a cap.
    """
    if cap <= 0:
        return 0.0
    return min(value / cap, 1.0)