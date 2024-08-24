import json
from typing import Any, Dict, List

def compare_json(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> float:
    total_score = 0
    total_weight = 0

    all_keys = set(obj1.keys()) | set(obj2.keys())

    for key in all_keys:
        weight = 1
        if key not in obj1 or key not in obj2:
            score = 0
        else:
            score = compare_values(obj1[key], obj2[key])
        
        total_score += score * weight
        total_weight += weight

    return (total_score / total_weight) * 100 if total_weight > 0 else 100

def compare_values(val1: Any, val2: Any) -> float:
    if type(val1) != type(val2):
        return 0
    
    if isinstance(val1, dict):
        return compare_json(val1, val2) / 100
    elif isinstance(val1, list):
        return compare_lists(val1, val2)
    elif isinstance(val1, (int, float)):
        return 1 - min(abs(val1 - val2) / max(abs(val1), abs(val2), 1), 1)
    elif isinstance(val1, str):
        return string_similarity(val1, val2)
    elif isinstance(val1, bool):
        return 1 if val1 == val2 else 0
    else:
        return 0  # Unsupported type

def compare_lists(list1: List[Any], list2: List[Any]) -> float:
    if len(list1) == 0 and len(list2) == 0:
        return 1
    if len(list1) == 0 or len(list2) == 0:
        return 0
    
    scores = []
    for item1 in list1:
        best_score = max(compare_values(item1, item2) for item2 in list2)
        scores.append(best_score)
    
    for item2 in list2:
        best_score = max(compare_values(item1, item2) for item1 in list1)
        scores.append(best_score)
    
    return sum(scores) / len(scores)

def string_similarity(s1: str, s2: str) -> float:
    if len(s1) == 0 and len(s2) == 0:
        return 1
    if len(s1) == 0 or len(s2) == 0:
        return 0
    
    return 1 - (sum(c1 != c2 for c1, c2 in zip(s1, s2)) + abs(len(s1) - len(s2))) / max(len(s1), len(s2))
