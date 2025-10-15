import unittest
import os
from fractions import Fraction

from fraction_utils import FractionUtils
from expression_utils import ExpressionUtils
import arithmetic_generator as ag


class TestFractionUtils(unittest.TestCase):
    def test_string_roundtrip_integer(self):
        f = Fraction(5, 1)
        s = FractionUtils.fraction_to_string(f)
        self.assertEqual(s, '5')
        self.assertEqual(FractionUtils.string_to_fraction(s), f)

    def test_string_roundtrip_proper_fraction(self):
        f = Fraction(3, 5)
        s = FractionUtils.fraction_to_string(f)
        self.assertEqual(s, '3/5')
        self.assertEqual(FractionUtils.string_to_fraction(s), f)

    def test_string_roundtrip_mixed(self):
        f = Fraction(2*8+3, 8)  # 2'3/8
        s = FractionUtils.fraction_to_string(f)
        self.assertEqual(s, "2'3/8")
        self.assertEqual(FractionUtils.string_to_fraction(s), f)

    def test_valid_subtraction(self):
        a = Fraction(5, 4)
        b = Fraction(1, 4)
        self.assertTrue(FractionUtils.is_valid_subtraction(a, b))
        self.assertFalse(FractionUtils.is_valid_subtraction(b, a))

    def test_valid_division_proper_fraction(self):
        a = Fraction(1, 2)
        b = Fraction(3, 2)
        self.assertTrue(FractionUtils.is_valid_division(a, b))  # 1/2 ÷ 3/2 = 1/3 < 1
        self.assertFalse(FractionUtils.is_valid_division(b, a))  # 3/2 ÷ 1/2 = 3 > 1


class TestExpressionUtils(unittest.TestCase):
    def test_generate_expression_non_negative(self):
        for _ in range(200):
            expr = ExpressionUtils.generate_expression(10, 3)
            val = FractionUtils.calculate_expression(expr)
            self.assertGreaterEqual(val, 0)

    def test_generate_expression_operator_count(self):
        expr = ExpressionUtils.generate_expression(10, 3)
        count = sum(expr.count(op) for op in ['+', '-', '×', '÷'])
        # 运算符个数不超过3个
        self.assertLessEqual(count, 3)

    def test_normalization_commute_plus(self):
        e1 = "1 + 2 + 3"
        e2 = "3 + (2 + 1)"
        h1 = ExpressionUtils.get_expression_hash(e1)
        h2 = ExpressionUtils.get_expression_hash(e2)
        self.assertEqual(h1, h2)

    def test_normalization_not_associative(self):
        # 1+2+3 vs 3+2+1 在文档中不视为重复
        e1 = "1 + 2 + 3"
        e2 = "(3 + 2) + 1"
        h1 = ExpressionUtils.get_expression_hash(e1)
        h2 = ExpressionUtils.get_expression_hash(e2)
        self.assertNotEqual(h1, h2)

    def test_unique_generation(self):
        exprs = ExpressionUtils.generate_unique_expressions(100, 10, 3)
        self.assertEqual(len(exprs), 100)
        self.assertEqual(len(set(ExpressionUtils.get_expression_hash(e) for e in exprs)), 100)

    def test_answer_format_and_calc(self):
        expr = "1/6 + 1/8"
        ans = ExpressionUtils.calculate_answer(expr)
        self.assertEqual(ans, '7/24')


class TestGrading(unittest.TestCase):
    def test_generate_and_grade(self):
        exercises, answers = ag.generate_exercises(20, 10)
        ag.write_lines('Exercises.txt', exercises)
        ag.write_lines('Answers.txt', answers)
        ag.grade('Exercises.txt', 'Answers.txt', 'Grade.txt')
        self.assertTrue(os.path.exists('Grade.txt'))
        with open('Grade.txt', 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        # 所有答案应正确
        self.assertTrue(lines[0].startswith('Correct:'))
        self.assertIn('(1', lines[0])  # 包含编号列表
        self.assertEqual(lines[1], 'Wrong: 0 ()')


if __name__ == '__main__':
    unittest.main()