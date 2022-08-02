from typing import Callable, Optional


def get_relevant_value(values: list,
                       compr: Optional[Callable] = max) -> float:
    """
    Extracts the relevant value, by using a comparator.

    Parameters
    ----------
    values : list
        nested list, which somewhere include


    compr : func
        comperator function

    Returns
    -------
    float
        Relevant Failure value

    Examples
    --------

    You can use it for:

    - normal values and lists

       >>> values = [0.0, [1, 2, 3], [4, 5, 6]]
       Get the maximum value
       >>> get_relevant_value(values)
       return 6.0
       Get the minimum value
       >>> get_relevant_value(values, compr=min)
       return 0.0

    - dicts

       >>> failures = [{"max-stress": 2.0}, [{"max-stress": 1.0}, {"max-stress": 0.0}]]
       Get the maximum failure value
       >>> get_relevant_value(failures)
       return 2.0
    """
    result = []
    if isinstance(values, dict):
        return compr(list(dict(values).values()))

    for value in values:
        if isinstance(value, list):
            result.append(get_relevant_value(value, compr))
        elif isinstance(value, tuple):
            for val in value:
                result.append(get_relevant_value(val, compr))
        elif isinstance(value, dict):
            result += list(dict(value).values())
        else:
            result.append(value)

    return compr(result)
