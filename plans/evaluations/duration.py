
from functools import reduce
from typing import List
from random import Random

from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator
from plans.outcomes import Outcome, Status
from plans.context import Context
from .success import success_probability

from .outcomes import sample_outcome

def average_duration(p: Plan, n: int = 100) -> float: 
    if n <= 0: 
        raise ValueError(f"n {n} cannot be zero or negative")
    sum = 0.0
    for i in range(n): 
        outcome = sample_outcome(p) 
        sum += outcome.duration 
    return sum / n

def max_duration(p: Plan) -> int: 
    return MaxDurationEvaluator().evaluate_plan(p) 

class MaxDurationEvaluator(Evaluator[int]): 

    def evaluate_action(self, action: Action, c: Context = None) -> int:
        return action.duration.max_value()

    def evaluate_steps(self, steps: Steps, c: Context = None) -> int:
        children: List[int] = [self.evaluate_plan(p, c) for p in steps.children]
        if None in children: return None
        return sum(children) 
    
    def evaluate_requirements(self, reqs: Requirements, c: Context = None) -> int:
        children: List[int] = [self.evaluate_plan(p, c) for p in reqs.children]
        if None in children: return None
        return max(children)
    
    def evaluate_options(self, options: Options, c: Context = None) -> int:
        children: List[int] = [self.evaluate_plan(p, c) for p in options.children]
        if None in children: return None
        return sum(children)
    
    def evaluate_alternatives(self, alternatives: Alternatives, c: Context = None) -> int:
        children: List[int] = [self.evaluate_plan(p, c) for p in alternatives.children]
        if None in children: return None
        return sum(children)

    def evaluate_ensure(self, ensure: Ensure, c: Context = None) -> int:
        if success_probability(ensure.children[0]) < 1.0: 
            return None 
        else: 
            return self.evaluate_plan(ensure.children[0], c)
    
    def evaluate_loop(self, loop: Loop, c: Context = None) -> int:
        child_max = self.evaluate_plan(loop.children[0], c) 
        if child_max is None: return None
        return child_max * loop.max_loops
    
    def evaluate_optional(self, opt: Optional, c: Context = None) -> int:
        return self.evaluate_plan(opt.children[0], c)
    
    def evaluate_fail(self, failure: Fail, c: Context = None) -> int:
        return 0
    
    def evaluate_ifelse(self, ifelse: IfElse, c: Context = None) -> int: 
        children: List[int] = [self.evaluate_plan(p, c) for p in ifelse.children]
        if None in children: return None
        return children[0] + max(children[1], children[2])

