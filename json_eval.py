import json
from typing import Any, Dict, List, Tuple

class DifferenceReport:
    def __init__(self, expected_full_object = None):
        self.differences = []

    def add_difference(self, path: str, type: str, expected_value: Any, actual_value: Any):
        self.differences.append({
            "path": path,
            "type": type,
            "expected value": expected_value,
            "actual value": actual_value
        })

    def print_report(self):
        if not self.differences:
            print("No differences found.")
        else:
            print("Differences found:")
            for diff in self.differences:
                print(f"  Path: {diff['path']}")
                print(f"  Type: {diff['type']}")
                print(f"  Expected Value 1: {diff['expected value']}")
                print(f"  Actual Value 2: {diff['actual value']}")
                print()


def compare_json(expected: Dict[str, Any], actual: Dict[str, Any], path: str = "") -> Tuple[float, DifferenceReport]:
    total_score = 0
    total_weight = 0
    report = DifferenceReport()

    all_keys = set(expected.keys()) | set(actual.keys())

    for key in all_keys:
        weight = 1
        current_path = f"{path}.{key}" if path else key

        if key not in expected:
            report.add_difference(current_path, "Missing Key", "Not present", actual[key])
            score = 0
        elif key not in actual:
            report.add_difference(current_path, "Missing Key", expected[key], "Not present")
            score = 0
        else:
            score, sub_report = compare_values(expected[key], actual[key], current_path)
            report.differences.extend(sub_report.differences)
        
        total_score += score * weight
        total_weight += weight

    final_score = (total_score / total_weight) * 100 if total_weight > 0 else 100
    return final_score, report

def compare_values(expected_val: Any, actual_val: Any, path: str) -> Tuple[float, DifferenceReport]:
    report = DifferenceReport()

    if type(expected_val) != type(actual_val):
        report.add_difference(path, "Type Mismatch", type(expected_val).__name__, type(actual_val).__name__)
        return 0, report
    
    if isinstance(expected_val, dict):
        score, sub_report = compare_json(expected_val, actual_val, path)
        return score / 100, sub_report
    elif isinstance(expected_val, list):
        return compare_lists(expected_val, actual_val, path)
    elif isinstance(expected_val, (int, float)):
        score = 1 - min(abs(expected_val - actual_val) / max(abs(expected_val), abs(actual_val), 1), 1)
        if score < 1:
            report.add_difference(path, "Value Difference", expected_val, actual_val)
        return score, report
    elif isinstance(expected_val, str):
        score = string_similarity(expected_val, actual_val)
        if score < 1:
            report.add_difference(path, "String Difference", expected_val, actual_val)
        return score, report
    elif isinstance(expected_val, bool):
        score = 1 if expected_val == actual_val else 0
        if score < 1:
            report.add_difference(path, "Boolean Difference", expected_val, actual_val)
        return score, report
    else:
        report.add_difference(path, "Unsupported Type", type(expected_val).__name__, type(actual_val).__name__)
        return 0, report


def compare_lists(expected_list: List[Any], actual_list: List[Any], path: str) -> Tuple[float, DifferenceReport]:
    report = DifferenceReport()

    if len(expected_list) == 0 and len(actual_list) == 0:
        return 1, report
    if len(expected_list) == 0 or len(actual_list) == 0:
        report.add_difference(path, "List Length Mismatch", len(expected_list), len(actual_list))
        return 0, report
    
    scores = []
    for i, item1 in enumerate(expected_list):
        best_score = 0
        best_report = DifferenceReport()
        for j, item2 in enumerate(actual_list):
            score, sub_report = compare_values(item1, item2, f"{path}[{i}]")
            if score > best_score:
                best_score = score
                best_report = sub_report
        scores.append(best_score)
        report.differences.extend(best_report.differences)
    
    for j, item2 in enumerate(actual_list):
        best_score = 0
        for i, item1 in enumerate(expected_list):
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
            #print(json_str)
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None
    else:
        print("No JSON object found in the string")
        return None


'''
The function does the following:

It defines a helper function set_nested to set values in nested dictionaries using a path string.
It iterates through the update_data dictionary.
For each path:

If the type is 'Value Difference', it finds the highest numeric value and sets it in the JSON object.
If the type is 'String Difference', it finds the most common string (the one with the highest count) and sets it in the JSON object.


It returns the updated JSON object.
'''
from typing import Dict, Any
def update_json_with_highest_values(json_obj: Dict[str, Any], update_data: Dict[str, Any]) -> Dict[str, Any]:
    def set_nested(obj, path, value):
        parts = path.replace(']', '').replace('[', '.').split('.')
        for part in parts[:-1]:
            if part.isdigit():
                part = int(part)
            obj = obj[part]
        last_part = parts[-1]
        if last_part.isdigit():
            last_part = int(last_part)
        obj[last_part] = value

    for path, data in update_data.items():
        if data['type'] == 'Value Difference':
            highest_value = max(data['values'].keys())
            set_nested(json_obj, path, highest_value)
        elif data['type'] == 'String Difference':
            highest_count = max(data['values'].values())
            most_common_string = next(key for key, value in data['values'].items() if value == highest_count)
            set_nested(json_obj, path, most_common_string)

    return json_obj