from monarch.core.haan import require_haan


def assemble(operator: str) -> str:
    require_haan(operator, "edit")
    return "HAAN accepted — Arena session assembles/cuts with generated assets."
