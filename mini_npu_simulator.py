from matrix import Matrix
from json_data_loader import JsonDataLoader
import time


class MiniNpuSimulator:
    def __init__(self):
        self.epsilon = 1e-9
        self.file_path = "data.json"
        self.result_record = []

    def run(self):
        print("=== Mini NPU Simulator ===\n")
        print("[모드 선택]\n")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")

        user_input = self.get_input_number("선택: ", [1, 2])
        if user_input is None:
            print("\n프로그램을 종료합니다.")
            return

        if user_input == 1:
            self.run_mode1()
        elif user_input == 2:
            self.run_mode2()

    def run_mode1(self):
        print("\n\n#----------------------------------------")
        print("# [1] 필터 입력")
        print("#----------------------------------------")

        filter_a = self.get_validated_input("필터 A (3줄 입력, 공백 구분)", 3)
        if filter_a is None:
            print("\n프로그램을 종료합니다.")
            return

        filter_b = self.get_validated_input("필터 B (3줄 입력, 공백 구분)", 3)
        if filter_b is None:
            print("\n프로그램을 종료합니다.")
            return

        print("\n\n#---------------------------------------")
        print("# [2] 패턴 입력")
        print("#---------------------------------------")

        pattern = self.get_validated_input("패턴 (3줄 입력, 공백 구분)", 3)
        if pattern is None:
            print("\n프로그램을 종료합니다.")
            return

        iterations = 10

        start_time = time.perf_counter()
        for _ in range(iterations):
            score_a = filter_a.mac(pattern)
            score_b = filter_b.mac(pattern)
        avg_time = ((time.perf_counter() - start_time) / iterations) * 1000

        diff = abs(score_a - score_b)
        is_undecided = diff < self.epsilon

        if is_undecided:
            print("\n\n#---------------------------------------")
            print("# [3] MAC 결과 (판정 불가)")
            print("#---------------------------------------")
            print(f"A('Cross') 점수: {score_a}")
            print(f"B('X') 점수: {score_b}")
            print("판정: 판정 불가 (|A-B| < 1e-9)")
            return

        result = "A" if score_a > score_b else "B"

        print("\n\n#---------------------------------------")
        print("# [3] MAC 결과")
        print("#---------------------------------------")
        print(f"A('Cross') 점수: {score_a}")
        print(f"B('X') 점수: {score_b}")
        print(f"연산 시간(평균/10회): {avg_time:.4f} ms")
        print(f"판정: {result}")

    def run_mode2(self):
        loader = JsonDataLoader(self.file_path)

        print("\n\n#---------------------------------------")
        print("# [1] 필터 로드")
        print("#---------------------------------------")

        try:
            filters_by_size = loader.load_filters()
            pattern_cases = loader.load_patterns()
        except (FileNotFoundError, ValueError) as exception:
            print(f"오류: {exception}")
            return

        for matrix_size in filters_by_size.keys():
            print(f"size_{matrix_size} 필터 로드 완료 (Cross, X)")

        print("\n\n#---------------------------------------")
        print("# [2] 패턴 분석 (라벨 정규화 적용)")
        print("#---------------------------------------")

        for pattern_case in pattern_cases:
            result = self.analyze_pattern_case(filters_by_size, pattern_case)
            self.result_record.append(result)
            self.print_pattern_result(result)

        print("\n\n#---------------------------------------")
        print("# [3] 성능 분석 (평균/10회)")
        print("#---------------------------------------")
        self.print_performance_analysis(filters_by_size, pattern_cases)

        print("\n\n#---------------------------------------")
        print("# [4] 결과 요약")
        print("#---------------------------------------")
        self.print_summary()

    def get_validated_input(self, prompt, matrix_size):
        print(prompt)
        rows = []

        while len(rows) < matrix_size:
            try:
                line = input().strip().split()

                if len(line) != matrix_size:
                    print(f"오류: 각 줄에 {matrix_size}개의 숫자를 입력해야 합니다. {len(rows) + 1}번째 줄을 다시 입력해주세요.")
                    continue

                row = []
                is_valid = True

                for value_text in line:
                    value = float(value_text)
                    if value not in [0.0, 1.0]:
                        print(f"오류: '0' 또는 '1'만 입력 가능합니다. {len(rows) + 1}번째 줄을 다시 입력해주세요.")
                        is_valid = False
                        break
                    row.append(value)

                if is_valid:
                    rows.append(row)

            except KeyboardInterrupt:
                return None
            except EOFError:
                return None
            except ValueError:
                print(f"오류: 잘못된 입력입니다. {len(rows) + 1}번째 줄을 다시 입력해주세요.")

        return Matrix(rows)

    def get_input_number(self, prompt, options):
        while True:
            try:
                value = input(prompt).strip()

                if not value:
                    print("입력이 비어있습니다.")
                    continue

                choice = int(value)
                if choice in options:
                    return choice

                print(f"{options} 중 하나를 선택해주세요.")

            except KeyboardInterrupt:
                return None
            except EOFError:
                return None
            except ValueError:
                print("숫자만 입력 가능합니다.")

    def decide_label(self, score_cross, score_x):
        if abs(score_cross - score_x) < self.epsilon:
            return "UNDECIDED"
        if score_cross > score_x:
            return "Cross"
        return "X"

    def measure_average_time(self, cross_filter, x_filter, pattern):
        iterations = 10

        start_time = time.perf_counter()
        for _ in range(iterations):
            cross_filter.mac(pattern)
            x_filter.mac(pattern)
        elapsed_time = time.perf_counter() - start_time

        return (elapsed_time / iterations) * 1000

    def analyze_pattern_case(self, filters_by_size, pattern_case):
        pattern_key = pattern_case["pattern_key"]
        matrix_size = pattern_case["size"]
        pattern = pattern_case["pattern"]
        expected = pattern_case["expected"]

        if matrix_size not in filters_by_size:
            return {
                "pattern_key": pattern_key,
                "score_cross": None,
                "score_x": None,
                "decision": "UNDECIDED",
                "expected": expected,
                "status": "FAIL",
                "reason": f"size_{matrix_size} 필터가 없습니다."
            }

        cross_filter = filters_by_size[matrix_size]["Cross"]
        x_filter = filters_by_size[matrix_size]["X"]

        try:
            cross_filter.validate_same_shape(pattern)
            x_filter.validate_same_shape(pattern)
        except ValueError as exception:
            return {
                "pattern_key": pattern_key,
                "score_cross": None,
                "score_x": None,
                "decision": "UNDECIDED",
                "expected": expected,
                "status": "FAIL",
                "reason": str(exception)
            }

        score_cross = cross_filter.mac(pattern)
        score_x = x_filter.mac(pattern)
        decision = self.decide_label(score_cross, score_x)

        if decision == "UNDECIDED":
            status = "FAIL"
            reason = "동점 규칙"
        elif decision == expected:
            status = "PASS"
            reason = None
        else:
            status = "FAIL"
            reason = "판정 결과가 expected와 다릅니다."

        return {
            "pattern_key": pattern_key,
            "score_cross": score_cross,
            "score_x": score_x,
            "decision": decision,
            "expected": expected,
            "status": status,
            "reason": reason
        }

    def print_pattern_result(self, result):
        print(f"--- {result['pattern_key']} ---")

        if result["score_cross"] is None or result["score_x"] is None:
            print("Cross 점수: 계산 불가")
            print("X 점수: 계산 불가")
        else:
            print(f"Cross 점수: {result['score_cross']}")
            print(f"X 점수: {result['score_x']}")

        if result["status"] == "PASS":
            print(f"판정: {result['decision']} | expected: {result['expected']} | PASS")
        else:
            print(f"판정: {result['decision']} | expected: {result['expected']} | FAIL ({result['reason']})")

    def find_first_pattern_by_size(self, pattern_cases, target_size):
        for pattern_case in pattern_cases:
            if pattern_case["size"] == target_size:
                return pattern_case["pattern"]
        return None

    def print_performance_analysis(self, filters_by_size, pattern_cases):
        print("크기       평균 시간(ms)    연산 횟수")
        print("-------------------------------------")

        sample_3_cross = Matrix([
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 0.0]
        ])
        sample_3_x = Matrix([
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0]
        ])
        sample_3_pattern = Matrix([
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0]
        ])

        avg_time_3 = self.measure_average_time(sample_3_cross, sample_3_x, sample_3_pattern)
        print(f"3x3        {avg_time_3:>10.4f} {sample_3_pattern.operation_count():>12}")

        for matrix_size in [5, 13, 25]:
            if matrix_size not in filters_by_size:
                continue

            pattern = self.find_first_pattern_by_size(pattern_cases, matrix_size)
            if pattern is None:
                continue

            cross_filter = filters_by_size[matrix_size]["Cross"]
            x_filter = filters_by_size[matrix_size]["X"]

            avg_time = self.measure_average_time(cross_filter, x_filter, pattern)
            print(f"{matrix_size}x{matrix_size:<7} {avg_time:>10.4f} {pattern.operation_count():>12}")

    def print_summary(self):
        total_count = len(self.result_record)
        pass_count = 0
        fail_count = 0
        fail_results = []

        for result in self.result_record:
            if result["status"] == "PASS":
                pass_count += 1
            else:
                fail_count += 1
                fail_results.append(result)

        print(f"총 테스트: {total_count}개")
        print(f"통과: {pass_count}개")
        print(f"실패: {fail_count}개")

        if fail_count == 0:
            return

        print("\n실패 케이스:")
        for fail_result in fail_results:
            print(f"- {fail_result['pattern_key']}: {fail_result['reason']}")