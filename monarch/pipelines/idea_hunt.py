from monarch.core.gates import gate_idea
from monarch.schemas import Idea


def hunt_from_candidates(ideas: list[Idea]) -> list[Idea]:
    ok = []
    for i in ideas:
        gate_idea(i)
        ok.append(i)
    return ok
