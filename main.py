import time

class MiniNpuSimulator:
    def __init__(self):
        self.epsilon = 1e-9
        self.result_record = []
    
    def run_mode1(self):
        print("\n\n#----------------------------------------")
        print("# [1] 필터 입력")
        print("#----------------------------------------")
        
        filter_a = self.get_validated_input("필터 A (3줄 입력, 공백 구분)", 3)
        filter_b = self.get_validated_input("필터 B (3줄 입력, 공백 구분)", 3)

        print("\n\n#---------------------------------------")
        print("# [2] 패턴 입력")
        print("#---------------------------------------")
        pattern = self.get_validated_input("패턴 (3줄 입력, 공백 구분)", 3)

        iterations = 10

        start_time = time.perf_counter()
        for _ in range(iterations):
            score_a = self.calculate_mac(filter_a, pattern)
            score_b = self.calculate_mac(filter_b, pattern)
        avg_time = ((time.perf_counter() - start_time) / 10) * 1000

        diff = abs(score_a - score_b)
        is_undecided = diff < self.epsilon
        if not is_undecided:
            result = 'A' if score_a > score_b else 'B'

        if is_undecided:
            print("\n\n#---------------------------------------")
            print("# [3] MAC 결과 (판정 불가)")
            print("#---------------------------------------")

            print(f"A('Cross') 점수: {score_a}")
            print(f"B('X') 점수: {score_b}")
            print("판정: 판정 불가 (|A-B| < 1e-9)")
        else:
            print("\n\n#---------------------------------------")
            print("# [3] MAC 결과")
            print("#---------------------------------------")

            print(f"A('Cross') 점수: {score_a}")        
            print(f"B('X') 점수: {score_b}")
            print(f"연산 시간(평균/10회): {avg_time:.4f} ms")
            print(f"판정: {result}")

    def calculate_mac(self, filter, pattern):
        sum = 0.0
        for i in range(len(pattern)):
            for j in range(len(pattern[i])):
                sum += filter[i][j] * pattern[i][j]
        return sum
    
    def get_validated_input(self, prompt, filter_size):
        print(prompt)
        matrix = []

        while len(matrix) < filter_size:
            try:
                line = input().strip().split()
                
                if len(line) != filter_size:
                    print(f"오류: 각 줄에 {filter_size}개의 숫자를 입력해야 합니다. {len(matrix) + 1}번째 줄을 다시 입력해주세요.")
                    continue

                row = []
                is_valid = True
                for x in line:
                    value = float(x)
                    if not value in [0.0, 1.0]:
                        print(f"오류: '0' 또는 '1'만 입력 가능합니다. {len(matrix) + 1}번째 줄을 다시 입력해주세요.")
                        is_valid = False
                        break
                    row.append(value)
                
                if is_valid:
                    matrix.append(row)
            except ValueError:
                print(f"오류: 잘못된 입력입니다. {len(matrix) + 1}번째 줄을 다시 입력해주세요.")
        
        return matrix

    def run(self):
        print("=== Mini NPU Simulator ===\n")
        print("[모드 선택]\n")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        user_input = self.get_input_number("선택: ", [1, 2])

        if user_input == 1:
            self.run_mode1()
       
    
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
            except ValueError:
                print("숫자만 입력 가능합니다.")

if __name__ == '__main__':
    npu = MiniNpuSimulator()
    npu.run()