class Matrix:
    def __init__(self, values):
        self._values = values
        
    def values(self):
        return self._values
    
    def size(self):
        return len(self._values)
    
    def operation_count(self):
        return self.size() * self.size()

    def sum(self):
        total = 0.0
        for row in self._values:
            for value in row:
                total += value
        return total
    
    def mac(self, other: "Matrix"):
        self.validate_same_shape(other)

        total = 0.0
        for row_index in range(self.size()):
            for column_index in range(len(self._values[row_index])):
                total += self._values[row_index][column_index] * other._values[row_index][column_index]
        return total

    def validate_same_shape(self, other: "Matrix"):
        if self.size() != other.size():
            raise ValueError("Matrix 크기가 다릅니다.")

        for row_index in range(self.size()):
            if len(self._values[row_index]) != len(other._values[row_index]):
                raise ValueError("Matrix 크기가 다릅니다.")