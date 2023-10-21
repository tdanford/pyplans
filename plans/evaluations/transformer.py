
from functools import reduce
from typing import List
from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, History, Evaluator
from plans.context import Context

class PlanTransformer(Evaluator[Plan]): 

    def evaluate_action(self, action: Action, c: Context) -> Plan:
        return action 

    def evaluate_steps(self, steps: Steps, c: Context) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p, c) for p in steps.children]
        return Steps(
            steps.name, *children
        )
    
    def evaluate_requirements(self, reqs: Requirements, c: Context) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p, c) for p in reqs.children]
        return Requirements(
            reqs.name, *children
        )
    
    def evaluate_options(self, options: Options, c: Context) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p, c) for p in options.children]
        return Options(
            options.name, *children
        )
    
    def evaluate_alternatives(self, alternatives: Alternatives, c: Context) -> Plan:
        children: List[Plan] = [self.evaluate_plan(p, c) for p in alternatives.children]
        return Alternatives(
            alternatives.name, *children
        )

    def evaluate_ensure(self, ensure: Ensure, c: Context) -> Plan:
        p_child = self.evaluate_plan(ensure.children[0], c) 
        return Ensure(p_child, name=ensure.name)
    
    def evaluate_loop(self, loop: Loop, c: Context) -> Plan:
        return Loop(
            self.evaluate_plan(loop.children[0], c), 
            loop.max_loops, 
            name=loop.name
        )
    
    def evaluate_optional(self, opt: Optional, c: Context) -> Plan:
        return Optional(
            self.evaluate_plan(opt.children[0], c), 
            name=opt.name
        )
    
    def evaluate_fail(self, failure: Fail, c: Context) -> Plan:
        return failure
    
    def evaluate_ifelse(self, ifelse: IfElse, c: Context) -> Plan: 
        children: List[Plan] = [self.evaluate_plan(p, c) for p in ifelse.children]
        return IfElse(
            children[0], 
            children[1], 
            children[2], 
            name=ifelse.name
        )

class EnsureAction(PlanTransformer): 
    """Transforms every Action in the tree, into an Ensure(Action)"""
    def evaluate_action(self, action: Action, c: Context) -> Plan: 
        return Ensure(action)  

# I want to build a RemainingPlan transformer, which transforms 
# (Plan x History) -> Plan, where the output plan is the *plan that 
# remains unfinished* given a particular History of Events
# ... but I don't know how, yet.
