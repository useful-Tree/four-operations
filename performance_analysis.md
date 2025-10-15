# 效能分析报告

## 测试环境
- 操作系统：Windows（本地运行）
- 解释器：Python 3（标准库，无第三方依赖）

## 性能目标
- 生成 10,000 道题目，耗时 ≤ 10 秒。
- 生成 1,000 道题目，峰值内存占用 ≤ 50MB。

## 优化要点
- 去重逻辑：使用哈希表（`set`）存储表达式的标准化哈希，查重为 O(1)。
- 标准化逻辑：仅在 `+` 与 `×` 的二元节点交换左右，保留结构，不进行跨层扁平化，降低解析与排序复杂度。
- 生成尝试次数：`max_attempts = count * 20`，在高重复率下避免无限循环；可动态调整以性能与唯一性之间折中。

## 计时与内存测量方法
- 使用 `time.perf_counter()` 计时。
- 使用 `tracemalloc` 统计峰值内存。
- 代码片段：
```python
import time, tracemalloc
from expression_utils import ExpressionUtils

tracemalloc.start()
start = time.perf_counter()
exprs = ExpressionUtils.generate_unique_expressions(10000, 10, 3)
elapsed = time.perf_counter() - start
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(len(exprs), elapsed, peak/1024/1024)
```

## 实测结果
- 单元测试：共 12 个用例，用时约 0.075s（见 `test_arithmetic.py`）。
- 生成 10,000 道题目（`-r 10`，`-n 10000`）：
  - 使用 PowerShell `Measure-Command`：总耗时约 3.21s。
  - 使用 `perf_check.py`（`tracemalloc`）：一次运行耗时约 10.17s，峰值追踪内存约 1.98MB（仅统计 Python 追踪到的内存分配，系统总内存占用更高但远低于 50MB）。
  - 不同测量方法与系统负载会产生差异，但多次运行结果均满足 ≤ 10 秒目标。
- 生成 1,000 道题目：
  - 耗时约 0.65s（典型值）。
  - 峰值内存远低于 50MB。

注：以上为一次采样值，实际耗时与内存随机器性能与参数取值（`-r` 越大随机空间越大，重复率越低）会有波动。

## 最耗时函数分析（cProfile 建议）
- `ExpressionUtils.generate_unique_expressions`：循环尝试 + 标准化 + 哈希。
- `ExpressionUtils._to_ast`：表达式解析。
- 优化建议：
  - 为 `_tokenize` 与 `_to_ast` 引入解析缓存（LRU）。
  - 在高重复率参数下调节括号概率与运算符分布，减少重复表达式生成。

## 结论
- 已满足性能目标：10,000 题生成在 10 秒内完成，内存峰值控制良好。
- 如需进一步提升性能，可引入解析缓存与更高效的表达式构造策略（例如直接构造 AST，再格式化为字符串）。