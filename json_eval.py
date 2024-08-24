import json
from typing import Any, Dict, List, Tuple

class DifferenceReport:
    def __init__(self):
        self.differences = []

    def add_difference(self, path: str, type: str, value1: Any, value2: Any):
        self.differences.append({
            "path": path,
            "type": type,
            "value1": value1,
            "value2": value2
        })

    def print_report(self):
        if not self.differences:
            print("No differences found.")
        else:
            print("Differences found:")
            for diff in self.differences:
                print(f"  Path: {diff['path']}")
                print(f"  Type: {diff['type']}")
                print(f"  Value 1: {diff['value1']}")
                print(f"  Value 2: {diff['value2']}")
                print()

def compare_json(obj1: Dict[str, Any], obj2: Dict[str, Any], path: str = "") -> Tuple[float, DifferenceReport]:
    total_score = 0
    total_weight = 0
    report = DifferenceReport()

    all_keys = set(obj1.keys()) | set(obj2.keys())

    for key in all_keys:
        weight = 1
        current_path = f"{path}.{key}" if path else key

        if key not in obj1:
            report.add_difference(current_path, "Missing Key", "Not present", obj2[key])
            score = 0
        elif key not in obj2:
            report.add_difference(current_path, "Missing Key", obj1[key], "Not present")
            score = 0
        else:
            score, sub_report = compare_values(obj1[key], obj2[key], current_path)
            report.differences.extend(sub_report.differences)
        
        total_score += score * weight
        total_weight += weight

    final_score = (total_score / total_weight) * 100 if total_weight > 0 else 100
    return final_score, report

def compare_values(val1: Any, val2: Any, path: str) -> Tuple[float, DifferenceReport]:
    report = DifferenceReport()

    if type(val1) != type(val2):
        report.add_difference(path, "Type Mismatch", type(val1).__name__, type(val2).__name__)
        return 0, report
    
    if isinstance(val1, dict):
        score, sub_report = compare_json(val1, val2, path)
        return score / 100, sub_report
    elif isinstance(val1, list):
        return compare_lists(val1, val2, path)
    elif isinstance(val1, (int, float)):
        score = 1 - min(abs(val1 - val2) / max(abs(val1), abs(val2), 1), 1)
        if score < 1:
            report.add_difference(path, "Value Difference", val1, val2)
        return score, report
    elif isinstance(val1, str):
        score = string_similarity(val1, val2)
        if score < 1:
            report.add_difference(path, "String Difference", val1, val2)
        return score, report
    elif isinstance(val1, bool):
        score = 1 if val1 == val2 else 0
        if score < 1:
            report.add_difference(path, "Boolean Difference", val1, val2)
        return score, report
    else:
        report.add_difference(path, "Unsupported Type", type(val1).__name__, type(val2).__name__)
        return 0, report


def compare_lists(list1: List[Any], list2: List[Any], path: str) -> Tuple[float, DifferenceReport]:
    report = DifferenceReport()

    if len(list1) == 0 and len(list2) == 0:
        return 1, report
    if len(list1) == 0 or len(list2) == 0:
        report.add_difference(path, "List Length Mismatch", len(list1), len(list2))
        return 0, report
    
    scores = []
    for i, item1 in enumerate(list1):
        best_score = 0
        best_report = DifferenceReport()
        for j, item2 in enumerate(list2):
            score, sub_report = compare_values(item1, item2, f"{path}[{i}]")
            if score > best_score:
                best_score = score
                best_report = sub_report
        scores.append(best_score)
        report.differences.extend(best_report.differences)
    
    for j, item2 in enumerate(list2):
        best_score = 0
        for i, item1 in enumerate(list1):
            score, _ = compare_values(item1, item2, f"{path}[{j}]")
            if score > best_score:
                best_score = score
        scores.append(best_score)
    
    return sum(scores) / len(scores), report

def string_similarity(s1: str, s2: str) -> float:
    if len(s1) == 0 and len(s2) == 0:
        return 1
    if len(s1) == 0 or len(s2) == 0:
        return 0
    
    return 1 - (sum(c1 != c2 for c1, c2 in zip(s1, s2)) + abs(len(s1) - len(s2))) / max(len(s1), len(s2))

# Example usage
json1 = json.loads('{"name": "John", "age": 30, "city": "New York", "hobbies": ["reading", "swimming"], "details": {"height": 180, "weight": 75}}')
json2 = json.loads('{"name": "Jon", "age": 31, "city": "New York", "hobbies": ["reading", "running"], "details": {"height": 182, "weight": 78}}')


def extract_json_from_string(input_string):
    import json
    import re
    json_str = None
    start_index = input_string.find('{')
    if start_index != -1:
        # Initialize counters for matching braces
        open_braces = 0
        for i in range(start_index, len(input_string)):
            if input_string[i] == '{':
                open_braces += 1
            elif input_string[i] == '}':
                open_braces -= 1
                if open_braces == 0:
                    end_index = i + 1
                    json_str = input_string[start_index:end_index]
                    break

    if json_str:
        try:
            # Load the JSON object
            print(json_str)
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None
    else:
        print("No JSON object found in the string")
        return None