import json
from matrix import Matrix

class JsonDataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def load_data(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as exception:
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.file_path}") from exception
        except json.JSONDecodeError as exception:
            raise ValueError("JSON 형식이 올바르지 않습니다") from exception
            
    def load_filters(self):
        data = self.load_data()

        if "filters" not in data:
            raise ValueError("data.json에 filters 키가 없습니다.")
        
        raw_filters = data["filters"]
        filters_by_size = {}
        
        for size_key, filters in raw_filters.items():
            matrix_size = self.extract_filter_size(size_key)
            
            if not isinstance(filters, dict):
                raise ValueError(f"{size_key}의 값은 객체여야 합니다.")

            if "cross" not in filters:
                raise ValueError(f"{size_key}에 cross 필터가 없습니다.")

            if "x" not in filters:
                raise ValueError(f"{size_key}에 x 필터가 없습니다.")
            
            cross_matrix = Matrix(filters["cross"])
            x_matrix = Matrix(filters["x"])
            
            filters_by_size[matrix_size] = {
                "cross": cross_matrix,
                "x": x_matrix
            }
        
        return filters_by_size

    def load_patterns(self):
        data = self.load_data()
        
        if "patterns" not in data:
            raise ValueError("data.json에 patterns 키가 없습니다.")
            
        raw_patterns = data["patterns"]
        pattern_cases = []
        
        for pattern_key, pattern_info in raw_patterns.items():
            matrix_size = self.extract_pattern_size(pattern_key)
            
            if not isinstance(pattern_info, dict):
                raise ValueError(f"{pattern_key}의 값은 객체여야 합니다.")

            if "input" not in pattern_info:
                raise ValueError(f"{pattern_key}에 input 키가 없습니다.")

            if "expected" not in pattern_info:
                raise ValueError(f"{pattern_key}에 expected 키가 없습니다.")
            
            pattern_matrix = Matrix(pattern_info["input"])
            expected = pattern_info["expected"]
            
            pattern_cases.append({
                "pattern_key": pattern_key,
                "size": matrix_size,
                "pattern": pattern_matrix,
                "expected": expected
            })
        
        return pattern_cases
    
    def extract_filter_size(self, size_key):
        parts = size_key.split("_")
        
        if len(parts) != 2 or parts[0] != "size":
            raise ValueError(f"잘못된 filter 키 형식입니다: {size_key}")
        
        try:
            return int(parts[1])
        except ValueError as exception:
            raise ValueError(f"filter 크기를 숫자로 변환할 수 없습니다: {size_key}") from exception
    
    def extract_pattern_size(self, pattern_key):
        parts = pattern_key.split("_")
        
        if len(parts) != 3 or parts[0] != "size":
            raise ValueError(f"잘못된 pattern 키 형식입니다: {pattern_key}")
        
        try:
            return int(parts[1])
        except ValueError as exception:
            raise ValueError(f"filter 크기를 숫자로 변환할 수 없습니다: {pattern_key}") from exception