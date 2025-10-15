"""
表达式工具类
处理表达式生成、括号处理和去重逻辑
"""

import random
import hashlib
from dataclasses import dataclass
from typing import List, Union
from fractions import Fraction
from fraction_utils import FractionUtils


class ExpressionUtils:
    """表达式工具类，处理表达式生成和去重"""

    OPERATORS = ['+', '-', '×', '÷']

    @staticmethod
    def generate_simple_expression(max_value):
        """
        生成简单表达式（两个操作数），满足：
        - 减法不产生负数
        - 除法结果为真分数（0<结果<1）
        """
        num1 = FractionUtils.generate_number(max_value)
        num2 = FractionUtils.generate_number(max_value)

        operator = random.choice(ExpressionUtils.OPERATORS)

        if operator == '-':
            # 确保不产生负数
            if not FractionUtils.is_valid_subtraction(num1, num2):
                num1, num2 = num2, num1
            if not FractionUtils.is_valid_subtraction(num1, num2):
                operator = '+'
        elif operator == '÷':
            # 保证除法得到真分数
            if not FractionUtils.is_valid_division(num1, num2):
                if FractionUtils.is_valid_division(num2, num1):
                    num1, num2 = num2, num1
                else:
                    operator = '×'

        num1_str = FractionUtils.fraction_to_string(num1)
        num2_str = FractionUtils.fraction_to_string(num2)
        expression = f"{num1_str} {operator} {num2_str}"

        return expression, True

    @staticmethod
    def generate_complex_expression(max_value, max_operators=3):
        """
        生成复杂表达式（多个操作数），逐步构造并在 '-' 与 '÷' 时强制括号，保证子表达式合法。
        """
        num_operators = random.randint(2, max_operators)

        # 初始操作数
        current_value = FractionUtils.generate_number(max_value)
        expression = FractionUtils.fraction_to_string(current_value)

        for _ in range(num_operators):
            operator = random.choice(ExpressionUtils.OPERATORS)

            # 生成满足约束的下一个操作数
            attempts = 0
            while True:
                attempts += 1
                next_value = FractionUtils.generate_number(max_value)
                if operator == '-':
                    if FractionUtils.is_valid_subtraction(current_value, next_value):
                        break
                elif operator == '÷':
                    # 保证 (current_value) ÷ next_value 是真分数
                    if next_value != 0 and current_value > 0 and FractionUtils.is_valid_division(current_value, next_value):
                        break
                else:
                    break
                if attempts > 50:
                    operator = '+'
                    break

            next_str = FractionUtils.fraction_to_string(next_value)

            if operator in ['-', '÷']:
                expression = f"({expression}) {operator} {next_str}"
            else:
                if random.random() < 0.3:
                    expression = f"({expression}) {operator} {next_str}"
                else:
                    expression = f"{expression} {operator} {next_str}"

            # 更新当前值
            if operator == '+':
                current_value = current_value + next_value
            elif operator == '-':
                current_value = current_value - next_value
            elif operator == '×':
                current_value = current_value * next_value
            elif operator == '÷':
                current_value = current_value / next_value

        # 验证整体非负
        try:
            result = FractionUtils.calculate_expression(expression)
            if result < 0:
                return expression, False
        except Exception:
            return expression, False

        return expression, True

    @staticmethod
    def generate_expression(max_value, max_operators=3):
        """生成满足约束的表达式"""
        max_attempts = 50

        for _ in range(max_attempts):
            if random.random() < 0.4:
                expression, valid = ExpressionUtils.generate_simple_expression(max_value)
            else:
                expression, valid = ExpressionUtils.generate_complex_expression(max_value, max_operators)

            if valid and ExpressionUtils.is_expression_valid(expression):
                return expression

        # 兜底：简单加法
        num1 = FractionUtils.generate_number(max_value)
        num2 = FractionUtils.generate_number(max_value)
        num1_str = FractionUtils.fraction_to_string(num1)
        num2_str = FractionUtils.fraction_to_string(num2)
        return f"{num1_str} + {num2_str}"

    @staticmethod
    def is_expression_valid(expression):
        """验证表达式是否有效（整体非负）"""
        try:
            result = FractionUtils.calculate_expression(expression)
            return result >= 0
        except Exception:
            return False

    # ==== 解析与标准化（AST）用于去重 ====

    @dataclass
    class Node:
        pass

    @dataclass
    class Num(Node):
        token: str

    @dataclass
    class BinOp(Node):
        op: str
        left: 'ExpressionUtils.Node'
        right: 'ExpressionUtils.Node'

    @staticmethod
    def _tokenize(expr: str) -> List[str]:
        tokens = []
        cur = ''
        for ch in expr:
            if ch in '+-×÷()':
                if cur.strip():
                    tokens.append(cur.strip())
                    cur = ''
                tokens.append(ch)
            elif ch == ' ':
                if cur.strip():
                    tokens.append(cur.strip())
                    cur = ''
            else:
                cur += ch
        if cur.strip():
            tokens.append(cur.strip())
        return tokens

    @staticmethod
    def _precedence(op: str) -> int:
        return 2 if op in ['×', '÷'] else 1

    @staticmethod
    def _to_ast(tokens: List[str]) -> 'ExpressionUtils.Node':
        # Shunting-yard 转 AST
        output: List[ExpressionUtils.Node] = []
        ops: List[str] = []

        def apply_op():
            op = ops.pop()
            right = output.pop()
            left = output.pop()
            output.append(ExpressionUtils.BinOp(op, left, right))

        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t in '+-×÷':
                while ops and ops[-1] in '+-×÷' and ExpressionUtils._precedence(ops[-1]) >= ExpressionUtils._precedence(t):
                    apply_op()
                ops.append(t)
            elif t == '(':
                ops.append(t)
            elif t == ')':
                while ops and ops[-1] != '(':
                    apply_op()
                if ops and ops[-1] == '(':
                    ops.pop()
            else:
                # 规范化数字表示
                try:
                    frac = FractionUtils.string_to_fraction(t)
                    norm = FractionUtils.fraction_to_string(frac)
                except Exception:
                    norm = t
                output.append(ExpressionUtils.Num(norm))
            i += 1

        while ops:
            apply_op()

        return output[-1] if output else ExpressionUtils.Num('0')

    @staticmethod
    def _node_to_str(node: 'ExpressionUtils.Node') -> str:
        if isinstance(node, ExpressionUtils.Num):
            return node.token
        if isinstance(node, ExpressionUtils.BinOp):
            left_str = ExpressionUtils._node_to_str(node.left)
            right_str = ExpressionUtils._node_to_str(node.right)
            if node.op in ['+', '×']:
                # 仅在当前层交换左右，保持结构，不进行跨层扁平化，符合“有限次交换 + 与 × 左右表达式”的规则
                if left_str > right_str:
                    left_str, right_str = right_str, left_str
            # 始终保留括号来表示结构
            return f"({left_str}) {node.op} ({right_str})"
        return ''

    @staticmethod
    def normalize_expression(expression):
        """通过 AST 标准化表达式，+、× 的操作数排序，用于去重"""
        tokens = ExpressionUtils._tokenize(expression)
        ast = ExpressionUtils._to_ast(tokens)
        return ExpressionUtils._node_to_str(ast)

    @staticmethod
    def get_expression_hash(expression):
        normalized = ExpressionUtils.normalize_expression(expression)
        return hashlib.md5(normalized.encode()).hexdigest()

    @staticmethod
    def generate_unique_expressions(count, max_value, max_operators=3):
        expressions = []
        expression_hashes = set()
        max_attempts = count * 20
        attempts = 0

        while len(expressions) < count and attempts < max_attempts:
            attempts += 1
            expression = ExpressionUtils.generate_expression(max_value, max_operators)
            expr_hash = ExpressionUtils.get_expression_hash(expression)
            if expr_hash not in expression_hashes:
                expressions.append(expression)
                expression_hashes.add(expr_hash)
        return expressions

    @staticmethod
    def calculate_answer(expression):
        try:
            result = FractionUtils.calculate_expression(expression)
            return FractionUtils.fraction_to_string(result)
        except Exception:
            return "计算错误"

    @staticmethod
    def format_exercise(index, expression):
        return f"{index}. {expression} ="

    @staticmethod
    def format_answer(index, answer):
        return f"{index}. {answer}"