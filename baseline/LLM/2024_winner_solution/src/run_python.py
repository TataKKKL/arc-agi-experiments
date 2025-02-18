import json
import os
import subprocess
import sys
import tempfile
import time

from asyncer import asyncify
from devtools import debug
from pydantic import BaseModel

from src import logfire
from src.models import GRID


class PythonResult(BaseModel):
    stdout: str | None
    stderr: str | None
    return_code: int
    timed_out: bool
    latency_ms: float
    transform_results: list[GRID] | None


class PythonException(Exception):
    pass


def run_python_transform_sync(
    code: str, grid_lists: list[GRID], timeout: int, raise_exception: bool
) -> PythonResult:
    """
    Execute a Python string containing a transform function and call it with the provided grid.

    Args:
        code (str): Python code containing transform function
        grid_lists (List[List[List[int]]]): Input grids to transform
        timeout (int): Maximum execution time in seconds

    Returns:
        PythonResult containing execution results and transformed grid
    """
    # Wrap the code to call transform and serialize result
    wrapped_code = f"""
import json
import sys
import numpy as np
import scipy
from typing import List, Tuple, Set, Union, Optional

# Original code with transform function
{code}

# Input grid
grid_lists = {json.dumps(grid_lists)}

def to_python_array(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return to_python_array(obj.tolist())
    elif isinstance(obj, list):
        return [to_python_array(item) for item in obj]
    return obj

try:
    results: list[list[list[int]]] = []
    for grid_list in grid_lists:
        # Call transform and get result
        result = transform(grid_list)
        result = to_python_array(result)
        # Validate result type
        if not isinstance(result, list) or not all(isinstance(row, list) for row in result):
            print("Error: transform must return List[List[int]]", file=sys.stderr)
            sys.exit(1)
        results.append(result)
    # Print results as JSON
    print("TRANSFORM_RESULT:" + json.dumps(results))
except Exception as e:
    print("Error executing transform: " + str(e) + "RESULTS" + str(results) + "T", type(results), file=sys.stderr)
    sys.exit(1)
"""

    start = time.time()

    # Create a temporary file to store the code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(wrapped_code)
        temp_file = f.name

    try:
        # Run the Python process with timeout
        process = subprocess.Popen(
            [sys.executable, temp_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        transform_results = None
        timed_out = False

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return_code = process.returncode

            # Parse transform result from stdout if successful
            if return_code == 0 and stdout:
                for line in stdout.splitlines():
                    if line.startswith("TRANSFORM_RESULT:"):
                        try:
                            transform_results = json.loads(
                                line.replace("TRANSFORM_RESULT:", "", 1)
                            )
                        except json.JSONDecodeError:
                            stderr = "Error: Could not parse transform result"
                            return_code = 1

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            stderr = f"Execution timed out after {timeout} seconds"
            return_code = -1
            timed_out = True

        latency_ms = (time.time() - start) * 1000

        if not transform_results and raise_exception:
            raise PythonException(stderr)

        return PythonResult(
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            timed_out=timed_out,
            latency_ms=latency_ms,
            transform_results=transform_results,
        )

    finally:
        # Clean up the temporary file
        os.unlink(temp_file)


async def run_python_transform_async(
    code: str, grid_lists: list[GRID], timeout: int, raise_exception: bool
) -> PythonResult | None:
    try:
        result = await asyncify(run_python_transform_sync)(
            code=code,
            grid_lists=grid_lists,
            timeout=timeout,
            raise_exception=raise_exception,
        )
        return result
    except Exception as e:
        logfire.debug(f"ERROR RUNNING PYTHON: {e}")
        return None


class TransformInput(BaseModel):
    code: str
    grid_lists: list[GRID]
    timeout: int
    raise_exception: bool


async def run_python_transforms(
    inputs: list[TransformInput],
) -> list[PythonResult | None]:
    return await asyncio.gather(
        *[
            run_python_transform_async(
                input.code, input.grid_lists, input.timeout, input.raise_exception
            )
            for input in inputs
        ]
    )


async def main() -> None:
    for _ in range(10):
        print("running")
        result = await run_python_transform_async(
            _code, grid_lists=[test_grid, test_grid], timeout=5, raise_exception=False
        )
        print(result)
    print("NOW ON TO TASKS TESTING")
    tasks = [
        run_python_transform_async(
            _code, grid_lists=[test_grid, test_grid], timeout=5, raise_exception=False
        )
        for _ in range(10)
    ]

    results = await asyncio.gather(*tasks)
    print(results)


# Example usage
if __name__ == "__main__":
    # Example transform function that rotates the grid 90 degrees clockwise
    _code = """
def transform(grid_list: list[list[int]]) -> list[list[int]]:
    if not grid_list:
        return []
    # Rotate 90 degrees clockwise
    rows = len(grid_list)
    cols = len(grid_list[0])
    result = [[0] * rows for _ in range(cols)]

    for i in range(rows):
        for j in range(cols):
            result[j][rows - 1 - i] = grid_list[i][j]

    return result
"""

    # Test grid
    test_grid = [
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
        [
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            31,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
            1,
            2,
            3,
        ],
    ]

    for _ in range(10):
        print("running")
        result = run_python_transform_sync(
            _code, grid_lists=[test_grid, test_grid], timeout=5, raise_exception=False
        )
    import asyncio

    asyncio.run(main())
    # debug(result)

    # Expected output for test grid:
    # [
    #     [7, 4, 1],
    #     [8, 5, 2],
    #     [9, 6, 3]
    # ]
