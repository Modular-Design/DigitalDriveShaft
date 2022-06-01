from .ifalure import IFailure
from .imapdlfailure import IMAPDLFailure
from .maxstressfailure import MaxStressFailure
from .cuntzefailure import CuntzeFailure
from typing import List, Tuple


def extract_failures(failures: List[Tuple[dict, dict]], whitelist: List[str]) -> List[dict]:
    result = []
    for layers in failures:
        for layer in layers:
            for failure in whitelist:
                value = layer.get(failure)
                if value is not None:
                    result.append({failure: value})

    return result
