def total(prices: list[float]) -> float:
    return sum(prices)


def apply_discount(total: float, percent: float) -> float:
    return total - percent
