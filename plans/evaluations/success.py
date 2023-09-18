
from functools import reduce
from typing import List
from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator

def success_probability(p: Plan) -> float: 
    v = SuccessEvaluator()
    value = v.evaluate_plan(p) 
    return value 

class SuccessEvaluator(Evaluator[float]): 

    def evaluate_action(self, action: Action) -> float:
        return action.success_prob

    def success_conjunction(self, p: Plan) -> float:
        children: List[float] = [self.evaluate_plan(p) for p in p.children]
        return reduce(lambda x, y: x * y, children, 1.0) 

    def success_disjunction(self, p: Plan) -> float:
        children: List[float] = [self.evaluate_plan(p) for p in p.children]
        not_children = [1.0 - x for x in children]
        not_all = reduce(lambda x, y: x * y, not_children, 1.0) 
        return 1.0 - not_all

    def evaluate_steps(self, steps: Steps) -> float:
        return self.success_conjunction(steps)
    
    def evaluate_requirements(self, reqs: Requirements) -> float:
        return self.success_conjunction(reqs)
    
    def evaluate_options(self, options: Options) -> float:
        return self.success_disjunction(options) 

    def evaluate_alternatives(self, alternatives: Alternatives) -> float:
        return self.success_disjunction(alternatives)

    def evaluate_ensure(self, ensure: Ensure) -> float:
        p_child = self.evaluate_plan(ensure.children[0]) 
        if p_child <= 0.0: 
            raise ValueError("Cannot ENSURE the execution of a child plan with a 0 success probability")
        return 1.0
    
    def evaluate_loop(self, loop: Loop) -> float:
        child: float = self.evaluate_plan(loop.children[0])
        not_all = reduce(lambda x, y: x * y, (1.0 - child for i in range(loop.max_loops)), 1.0) 
        return 1.0 - not_all
    
    def evaluate_optional(self, opt: Optional) -> float:
        return 1.0
    
    def evaluate_fail(self, failure: Fail) -> float:
        return 0.0
    
    def evaluate_ifelse(self, ifelse: IfElse) -> float: 
        children: List[float] = [self.evaluate_plan(p) for p in ifelse.children]
        return children[0] * children[1] + (1.0 - children[0]) * children[2]

    
