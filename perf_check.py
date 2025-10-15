import time
import tracemalloc
from expression_utils import ExpressionUtils

def run(count=10000, r=10):
    tracemalloc.start()
    start = time.perf_counter()
    exprs = ExpressionUtils.generate_unique_expressions(count, r, 3)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"generated={len(exprs)} time_sec={elapsed:.6f} peak_mb={peak/1024/1024:.2f}")

if __name__ == "__main__":
    run()