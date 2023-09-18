
from functools import reduce
from typing import List
from random import Random

from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator
from plans.outcomes import Outcome, Status
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

    def evaluate_action(self, action: Action) -> int:
        return action.duration.max_value()

    def evaluate_steps(self, steps: Steps) -> int:
        children: List[int] = [self.evaluate_plan(p) for p in steps.children]
        if None in children: return None
        return sum(children) 
    
    def evaluate_requirements(self, reqs: Requirements) -> int:
        children: List[int] = [self.evaluate_plan(p) for p in reqs.children]
        if None in children: return None
        return max(children)
    
    def evaluate_options(self, options: Options) -> int:
        children: List[int] = [self.evaluate_plan(p) for p in options.children]
        if None in children: return None
        return sum(children)
    
    def evaluate_alternatives(self, alternatives: Alternatives) -> int:
        children: List[int] = [self.evaluate_plan(p) for p in alternatives.children]
        if None in children: return None
        return sum(children)

    def evaluate_ensure(self, ensure: Ensure) -> int:
        if success_probability(ensure.children[0]) < 1.0: 
            return None 
        else: 
            return self.evaluate_plan(ensure.children[0])
    
    def evaluate_loop(self, loop: Loop) -> int:
        child_max = self.evaluate_plan(loop.children[0]) 
        if child_max is None: return None
        return child_max * loop.max_loops
    
    def evaluate_optional(self, opt: Optional) -> int:
        return self.evaluate_plan(opt.children[0])
    
    def evaluate_fail(self, failure: Fail) -> int:
        return 0
    
    def evaluate_ifelse(self, ifelse: IfElse) -> int: 
        children: List[int] = [self.evaluate_plan(p) for p in ifelse.children]
        if None in children: return None
        return children[0] + max(children[1], children[2])

