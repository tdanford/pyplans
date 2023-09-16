
from functools import reduce
from typing import List
from random import Random

from plans.plan import Action, Fail, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail
from plans.visitor import Evaluator
from plans.outcomes import Outcome, Status

from .outcomes import sample_outcome

def average_duration(p: Plan, n: int = 100) -> Outcome: 
    if n <= 0: 
        raise ValueError(f"n {n} cannot be zero or negative")
    sum = 0.0
    for i in range(n): 
        outcome = sample_outcome(p) 
        sum += outcome.duration 
    return sum / n

