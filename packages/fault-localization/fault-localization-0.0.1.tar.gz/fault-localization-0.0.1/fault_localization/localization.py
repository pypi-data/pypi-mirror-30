"""Fault localization calculations."""


import collections


ExecutionCounts = collections.namedtuple(
    "ExecutionCounts",
    "positive_cases negative_cases"
)

LINE_EXECUTIONS = collections.defaultdict(
    lambda: ExecutionCounts(
        positive_cases=0,
        negative_cases=0,
    )
)


def update_executions(lines, failed, line_executions=LINE_EXECUTIONS):
    """Update line executions to reflect test results."""
    for line in lines:
        prev_executions = line_executions[line]
        line_executions[line] = ExecutionCounts(
            positive_cases=prev_executions.positive_cases + int(not failed),
            negative_cases=prev_executions.negative_cases + int(failed)
        )

