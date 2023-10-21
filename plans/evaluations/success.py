
from functools import reduce
from typing import List
from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator
from plans.context import Context 

def success_probability(p: Plan) -> float: 
    v = SuccessEvaluator()
    c = Context()
    value = v.evaluate_plan(p, c) 
    return value 

class SuccessEvaluator(Evaluator[float]): 

    def evaluate_action(self, action: Action, c: Context = None) -> float:
        return action.success_prob

    def success_conjunction(self, ps: List[Plan], c: Context = None) -> float:
        children: List[float] = [self.evaluate_plan(p, c) for p in ps]
        return reduce(lambda x, y: x * y, children) 

    def success_disjunction(self, ps: List[Plan], c: Context = None) -> float:
        children: List[float] = [self.evaluate_plan(p, c) for p in ps]
        not_children = [1.0 - x for x in children]
        not_all = reduce(lambda x, y: x * y, not_children) 
        return 1.0 - not_all

    def evaluate_steps(self, steps: Steps, c: Context = None) -> float:
        return self.success_conjunction(steps.children, c)
    
    def evaluate_requirements(self, reqs: Requirements, c: Context = None) -> float:
        return self.success_conjunction(reqs.children, c)
    
    def evaluate_options(self, options: Options, c: Context = None) -> float:
        print("evaluating options")
        return self.success_disjunction(options.children, c) 

    def evaluate_alternatives(self, alternatives: Alternatives, c: Context = None) -> float:
        return self.success_disjunction(alternatives.children, c)

    def evaluate_ensure(self, ensure: Ensure, c: Context = None) -> float:
        p_child = self.evaluate_plan(ensure.children[0], c) 
        if p_child <= 0.0: 
            raise ValueError("Cannot ENSURE the execution of a child plan with a 0 success probability")
        return 1.0
    
    def evaluate_loop(self, loop: Loop, c: Context = None) -> float:
        child: float = self.evaluate_plan(loop.children[0], c)
        not_all = reduce(lambda x, y: x * y, (1.0 - child for i in range(loop.max_loops)), 1.0) 
        return 1.0 - not_all
    
    def evaluate_optional(self, opt: Optional, c: Context = None) -> float:
        return 1.0
    
    def evaluate_fail(self, failure: Fail, c: Context = None) -> float:
        return 0.0
    
    def evaluate_ifelse(self, ifelse: IfElse, c: Context = None) -> float: 
        children: List[float] = [self.evaluate_plan(p, c) for p in ifelse.children]
        return children[0] * children[1] + (1.0 - children[0]) * children[2]

    
