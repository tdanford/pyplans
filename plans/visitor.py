
from plans.plan import Plan, Action, Steps, Requirements, Options, Ensure, IfElse, Fail, Optional
from typing import TypeVar, Generic, List, Dict

T = TypeVar('T')

class Evaluator(Generic[T]): 

    def evaluate_plan(self, plan: Plan) -> T: 
        if isinstance(plan, Action): 
            return self.evaluate_action(plan)
        elif isinstance(plan, Steps):
            return self.evaluate_steps(plan)
        elif isinstance(plan, Requirements):
            return self.evaluato_requirements(plan)
        elif isinstance(plan, Options):
            return self.evaluate_options(plan)
        elif isinstance(plan, Ensure):
            return self.evaluate_ensure(plan)
        elif isinstance(plan, IfElse): 
            return self.evaluate_ifelse(plan) 
        elif isinstance(plan, Fail): 
            return self.evaluate_fail(plan) 
        elif isinstance(plan, Optional): 
            return self.evaluate_optional(plan) 
        else: 
            raise ValueError(f"Unrecognized Plan type {plan.plan_type}")

    def evaluate_action(self, action: Action) -> T: 
        ... 

    def evaluate_steps(self, steps: Steps) -> T:
        ... 

    def evaluato_requirements(self, reqs: Requirements) -> T:
        ...

    def evaluate_options(self, options: Options) -> T: 
        ...

    def evaluate_ensure(self, ensure: Ensure) -> T: 
        ...
    
    def evaluate_ifelse(self, ifelse: IfElse) -> T: 
        ...

    def evaluate_fail(self, failure: Fail) -> T: 
        ...

    def evaluate_optional(self, opt: Optional) -> T: 
        ...
