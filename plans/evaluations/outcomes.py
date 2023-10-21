
from functools import reduce
from typing import List
from random import Random

from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator
from plans.outcomes import Outcome, Status
from plans.context import Context

def sample_outcome(p: Plan) -> Outcome: 
    v = OutcomeSampler()
    c = Context()
    value = v.evaluate_plan(p, c) 
    return value 

class OutcomeSampler(Evaluator[Outcome]): 

    rand: Random

    def __init__(self): 
        self.rand = Random()

    def evaluate_action(self, action: Action, c: Context = None) -> Outcome:
        return action.sample_outcome(self.rand)

    def evaluate_steps(self, steps: Steps, c: Context = None) -> Outcome:
        duration: int = 0 
        success: Status = Status.SUCCESS
        for child in steps.children: 
            child_outcome = self.evaluate_plan(child, c) 
            success = success & child_outcome.status 
            duration += child_outcome.duration 
            if not success: 
                break 
        return Outcome(
            success, 
            duration 
        )
    
    def evaluate_requirements(self, reqs: Requirements, c: Context = None) -> Outcome:
        children: List[Outcome] = [self.evaluate_plan(p, c) for p in reqs.children]
        statuses = [c.status for c in children]
        if Status.FAILURE in statuses: 
            duration = min([c.duration for c in children if not c.status])
            return Outcome(Status.FAILURE, duration) 
        else: 
            duration = max([c.duration for c in children])
            return Outcome(Status.SUCCESS, duration) 

    def evaluate_options(self, options: Options, c: Context = None) -> Outcome:
        duration: int = 0 
        success: Status = Status.FAILURE
        for child in options.children: 
            child_outcome = self.evaluate_plan(child, c) 
            success = success | child_outcome.status 
            duration += child_outcome.duration 
            if success: 
                break 
        return Outcome(
            success, 
            duration 
        )

    def evaluate_alternatives(self, alternatives: Alternatives, c: Context = None) -> Outcome:
        children: List[Outcome] = [self.evaluate_plan(p, c) for p in alternatives.children]
        statuses = [c.status for c in children]
        if Status.SUCCESS in statuses: 
            successful_indices = [i for i in range(len(children)) if children[i].status == Status.SUCCESS]
            successful_durations = [children[i].duration for i in successful_indices]
            duration = min(successful_durations)
            return Outcome(Status.SUCCESS, duration) 
        else: 
            duration = max([c.duration for c in children])
            return Outcome(Status.FAILURE, duration) 

    def evaluate_ensure(self, ensure: Ensure, c: Context = None) -> Outcome:
        child: Outcome = self.evaluate_plan(ensure.children[0], c)
        duration: int = child.duration 
        success: Status = child.status 
        while not success: 
            child = self.evaluate_plan(ensure.children[0], c)
            duration += child.duration 
            success = success | child.status 
        return Outcome(success, duration) 
    
    def evaluate_loop(self, loop: Loop, c: Context = None) -> Outcome:
        duration: int = 0
        for i in range(loop.max_loops):
            child: Outcome = self.evaluate_plan(loop.children[0], c)
            duration += child.duration 
            if child.status: 
                return Outcome(Status.SUCCESS, duration) 
        return Outcome(Status.FAILURE, duration) 
    
    def evaluate_ifelse(self, ifelse: IfElse, c: Context = None) -> Outcome:
        test_outcome: Outcome = self.evaluate_plan(ifelse.children[0], c) 
        outc: Outcome 
        if test_outcome.status: 
            outc = self.evaluate_plan(ifelse.children[1], c) 
        else: 
            outc = self.evaluate_plan(ifelse.children[2], c) 
        
        return Outcome(
            outc.status, 
            test_outcome.duration + outc.duration
        )
    
    def evaluate_fail(self, failure: Fail, c: Context = None) -> Outcome:
        return Outcome(Status.FAILURE, 0)
    
    def evaluate_optional(self, opt: Optional, c: Context = None) -> Outcome:
        outcome = self.evaluate_plan(opt, c) 
        return Outcome(Status.SUCCESS, outcome.duration)
