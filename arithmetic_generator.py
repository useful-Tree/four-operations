"""
小学四则运算题目命令行程序

功能：
- 生成不重复的四则运算题目，输出到 Exercises.txt 和 Answers.txt
- 判题：读取题目与答案文件，输出 Grade.txt

用法示例：
- 生成题目：python arithmetic_generator.py -r 10 -n 20
- 判题：python arithmetic_generator.py -e Exercises.txt -a Answers.txt
"""

import argparse
import os
from typing import List, Tuple

from expression_utils import ExpressionUtils
from fraction_utils import FractionUtils


def generate_exercises(n: int, r: int) -> Tuple[List[str], List[str]]:
    """生成 n 道题目与答案

    Args:
        n: 题目数量（最大 10000）
        r: 数值范围（必需）

    Returns:
        (exercises, answers): 两个等长列表
    """
    if r is None or r < 1:
        raise ValueError("必须通过 -r 指定数值范围，且为>=1的自然数")

    if n < 1 or n > 10000:
        raise ValueError("-n 范围为 1-10000")

    expressions = ExpressionUtils.generate_unique_expressions(n, r, max_operators=3)
    exercises = []
    answers = []

    for i, expr in enumerate(expressions, start=1):
        exercises.append(ExpressionUtils.format_exercise(i, expr))
        answers.append(ExpressionUtils.format_answer(i, ExpressionUtils.calculate_answer(expr)))

    return exercises, answers


def write_lines(path: str, lines: List[str]) -> None:
    """写入行到文件（覆盖）"""
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def read_exercise_line(line: str) -> Tuple[int, str]:
    """解析题目行，如："1. 1 + 2 ="

    Returns:
        (index, expression)
    """
    line = line.strip()
    if not line:
        raise ValueError("空行")
    # 分割编号
    try:
        idx_split = line.split(".", 1)
        idx = int(idx_split[0])
        rest = idx_split[1].strip()
    except Exception:
        raise ValueError(f"题目行格式错误：{line}")

    # 去掉结尾的 '='
    if rest.endswith("="):
        expr = rest[:-1].strip()
    else:
        expr = rest
    return idx, expr


def read_answer_line(line: str) -> Tuple[int, str]:
    """解析答案行，如："1. 3/5" 或 "2. 7"

    Returns:
        (index, answer_token)
    """
    line = line.strip()
    if not line:
        raise ValueError("空行")
    try:
        idx_split = line.split(".", 1)
        idx = int(idx_split[0])
        rest = idx_split[1].strip()
        return idx, rest
    except Exception:
        raise ValueError(f"答案行格式错误：{line}")


def grade(exercise_path: str, answer_path: str, output_path: str = "Grade.txt") -> None:
    """判题并输出结果到 Grade.txt"""
    if not os.path.exists(exercise_path):
        raise FileNotFoundError(f"题目文件不存在：{exercise_path}")
    if not os.path.exists(answer_path):
        raise FileNotFoundError(f"答案文件不存在：{answer_path}")

    # 读取题目
    with open(exercise_path, "r", encoding="utf-8") as f:
        exercise_lines = [line.rstrip("\n") for line in f]

    # 读取答案
    with open(answer_path, "r", encoding="utf-8") as f:
        answer_lines = [line.rstrip("\n") for line in f]

    # 建立答案字典
    answer_map = {}
    for line in answer_lines:
        try:
            idx, ans_token = read_answer_line(line)
            answer_map[idx] = ans_token
        except Exception:
            # 跳过不合法行
            continue

    correct = []
    wrong = []

    for line in exercise_lines:
        try:
            idx, expr = read_exercise_line(line)
        except Exception:
            continue

        # 计算表达式值
        value = FractionUtils.calculate_expression(expr)

        # 题目答案
        expected = FractionUtils.fraction_to_string(value)

        # 用户答案
        ans_token = answer_map.get(idx)
        if ans_token is None:
            wrong.append(idx)
            continue

        try:
            user_value = FractionUtils.string_to_fraction(ans_token)
        except Exception:
            wrong.append(idx)
            continue

        if user_value == value:
            correct.append(idx)
        else:
            wrong.append(idx)

    correct.sort()
    wrong.sort()

    result_lines = [
        f"Correct: {len(correct)} ({', '.join(map(str, correct))})",
        f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})",
    ]

    write_lines(output_path, result_lines)


def main():
    parser = argparse.ArgumentParser(
        description="自动生成小学四则运算题目（支持判题）",
    )
    parser.add_argument("-r", type=int, help="数值范围（必需，所有数值小于此值）")
    parser.add_argument("-n", type=int, default=10, help="题目数量（默认10，最大10000）")
    parser.add_argument("-e", type=str, help="题目文件路径（判题模式）")
    parser.add_argument("-a", type=str, help="答案文件路径（判题模式）")

    args = parser.parse_args()

    # 判题模式优先
    if args.e and args.a:
        grade(args.e, args.a)
        print("判题完成，结果已写入 Grade.txt")
        return

    # 生成模式需要 -r
    if args.r is None:
        parser.error("生成题目时必须提供 -r 参数，例如：python arithmetic_generator.py -r 10 -n 20")

    exercises, answers = generate_exercises(args.n, args.r)

    write_lines("Exercises.txt", exercises)
    write_lines("Answers.txt", answers)

    print(f"已生成 {len(exercises)} 道题目到 Exercises.txt，与答案到 Answers.txt")


if __name__ == "__main__":
    main()