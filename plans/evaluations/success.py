
from functools import reduce
from typing import List
from plans.plan import Action, Fail, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail
from plans.visitor import Evaluator 

def success_probability(p: Plan) -> float: 
    v = SuccessEvaluator()
    value = v.evaluate_plan(p) 
    return value 

class SuccessEvaluator(Evaluator[float]): 

    def evaluate_action(self, action: Action) -> float:
        return action.success_prob

    def evaluate_steps(self, steps: Steps) -> float:
        children: List[float] = [self.evaluate_plan(p) for p in steps.children]
        return reduce(lambda x, y: x * y, children, 1.0) 
    
    def evaluate_requirements(self, reqs: Requirements) -> float:
        children: List[float] = [self.evaluate_plan(p) for p in reqs.children]
        return reduce(lambda x, y: x * y, children, 1.0) 
    
    def evaluate_options(self, options: Options) -> float:
        children: List[float] = [self.evaluate_plan(p) for p in options.children]
        not_children = [1.0 - x for x in children]
        not_all = reduce(lambda x, y: x * y, not_children, 1.0) 
        return 1.0 - not_all

    def evaluate_ensure(self, ensure: Ensure) -> float:
        p_child = self.evaluate_plan(ensure.children[0]) 
        if p_child <= 0.0: 
            raise ValueError("Cannot ENSURE the execution of a child plan with a 0 success probability")
        return 1.0
    
    def evaluate_optional(self, opt: Optional) -> float:
        return 1.0
    
    def evaluate_fail(self, failure: Fail) -> float:
        return 0.0
    
    def evaluate_ifelse(self, ifelse: IfElse) -> float: 
        children: List[float] = [self.evaluate_plan(p) for p in ifelse.children]
        return children[0] * children[1] + (1.0 - children[0]) * children[2]

    
