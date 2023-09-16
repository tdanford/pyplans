
from functools import reduce
from typing import List
from plans.plan import Action, Fail, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, History
from plans.visitor import Evaluator 

class PlanTransformer(Evaluator[Plan]): 

    def evaluate_action(self, action: Action) -> Plan:
        return action 

    def evaluate_steps(self, steps: Steps) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p) for p in steps.children]
        return Steps(
            steps.name, *children
        )
    
    def evaluate_requirements(self, reqs: Requirements) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p) for p in reqs.children]
        return Requirements(
            reqs.name, *children
        )
    
    def evaluate_options(self, options: Options) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p) for p in options.children]
        return Options(
            options.name, *children
        )

    def evaluate_ensure(self, ensure: Ensure) -> Plan:
        p_child = self.evaluate_plan(ensure.children[0]) 
        return Ensure(p_child, name=ensure.name)
    
    def evaluate_optional(self, opt: Optional) -> Plan:
        return Optional(
            self.evaluate_plan(opt.children[0]), 
            name=opt.name
        )
    
    def evaluate_fail(self, failure: Fail) -> Plan:
        return failure
    
    def evaluate_ifelse(self, ifelse: IfElse) -> Plan: 
        children: List[Plan] = [self.evaluate_plan(p) for p in ifelse.children]
        return IfElse(
            children[0], 
            children[1], 
            children[2], 
            name=ifelse.name
        )

class EnsureAction(PlanTransformer): 
    """Transforms every Action in the tree, into an Ensure(Action)"""
    def evaluate_action(self, action: Action) -> Plan: 
        return Ensure(action)  

# I want to build a RemainingPlan transformer, which transforms 
# (Plan x History) -> Plan, where the output plan is the *plan that 
# remains unfinished* given a particular History of Events
# ... but I don't know how, yet.
