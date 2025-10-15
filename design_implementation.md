# 设计与实现文档

## 架构概览
- `fraction_utils.py`：分数工具，负责分数/带分数的生成、格式转换、合法性校验与表达式计算。
- `expression_utils.py`：表达式工具，负责表达式随机生成、括号插入、标准化（用于去重）、答案计算与格式化输出。
- `arithmetic_generator.py`：主程序，负责命令行解析、批量生成题目与答案、文件写入、判题统计。

## 关键函数与关系
- `FractionUtils.generate_number(max_value)`：生成自然数/真分数/带分数。
- `FractionUtils.is_valid_subtraction(a, b)`：`a >= b` 校验，确保不产生负数。
- `FractionUtils.is_valid_division(a, b)`：`0 < a/b < 1` 校验，确保除法子表达式为真分数。
- `FractionUtils.calculate_expression(expr_str)`：解析字符串表达式并计算值（替换 `×/÷` 为 `*/`，将数字转为 `Fraction`）。
- `ExpressionUtils.generate_expression(max_value, max_operators)`：生成符合约束的表达式，`-` 与 `÷` 子表达式强制加括号。
- `ExpressionUtils.normalize_expression(expression)`：构造 AST，针对 `+`、`×` 在当前层交换左右并保留括号，生成标准化字符串用于哈希去重。
- `arithmetic_generator.generate_exercises(n, r)`：批量生成题目与答案并格式化输出。
- `arithmetic_generator.grade(exercise_path, answer_path)`：读取题目与答案，计算正确与错误题号，输出 `Grade.txt`。

## 表达式生成流程（简化）
1. 随机选择生成简单表达式或复杂表达式。
2. 对于 `-` 与 `÷`：
   - 生成满足 `a>=b` 与 `0<a/b<1` 的操作数，否则退化为其他运算。
   - 强制插入括号确保子表达式约束不被其他运算破坏。
3. 多步构造：逐步追加运算符与操作数，更新当前值以快速检查非负。
4. 校验表达式整体非负，失败则重试或回退到简单加法兜底。

## 判题流程
1. 解析题目行：`index, expression = read_exercise_line(line)`，去除末尾 `=`。
2. 计算表达式值，格式化为字符串（最简分数或带分数）。
3. 从答案文件读取对应编号的答案，解析为 `Fraction` 比较。
4. 统计正确与错误，输出到 `Grade.txt`（编号按升序）。

## 去重哈希计算
- 解析表达式为 AST：使用改造的 Shunting-yard 算法处理运算符优先级与括号。
- 在每个 `+` / `×` 节点，仅交换左右使其字典序一致；保留括号以表达结构；禁止跨层扁平化（防止错误地将不同结合结构视为相同）。
- 将标准化字符串做 `md5` 哈希，写入 `set` 做 O(1) 去重判断。

## 设计取舍与边界情况
- 仅使用标准库，避免外部依赖；分数使用 `fractions.Fraction` 自动约分。
- 判题允许题目与答案文件存在空行与不合法行，解析时跳过以增强鲁棒性。
- 生成表达式设置最大尝试次数上限，保证在高重复率时仍能较快完成任务。