
from functools import reduce
from typing import List
from random import Random

from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator
from plans.outcomes import Outcome, Status

def sample_outcome(p: Plan) -> Outcome: 
    v = OutcomeSampler()
    value = v.evaluate_plan(p) 
    return value 

class OutcomeSampler(Evaluator[Outcome]): 

    rand: Random

    def __init__(self): 
        self.rand = Random()

    def evaluate_action(self, action: Action) -> Outcome:
        return action.sample_outcome(self.rand)

    def evaluate_steps(self, steps: Steps) -> Outcome:
        duration: int = 0 
        success: Status = Status.SUCCESS
        for child in steps.children: 
            child_outcome = self.evaluate_plan(child) 
            success = success & child_outcome.status 
            duration += child_outcome.duration 
            if not success: 
                break 
        return Outcome(
            success, 
            duration 
        )
    
    def evaluate_requirements(self, reqs: Requirements) -> Outcome:
        children: List[Outcome] = [self.evaluate_plan(p) for p in reqs.children]
        statuses = [c.status for c in children]
        if Status.FAILURE in statuses: 
            duration = min([c.duration for c in children if not c.status])
            return Outcome(Status.FAILURE, duration) 
        else: 
            duration = max([c.duration for c in children])
            return Outcome(Status.SUCCESS, duration) 

    def evaluate_options(self, options: Options) -> Outcome:
        duration: int = 0 
        success: Status = Status.FAILURE
        for child in options.children: 
            child_outcome = self.evaluate_plan(child) 
            success = success | child_outcome.status 
            duration += child_outcome.duration 
            if success: 
                break 
        return Outcome(
            success, 
            duration 
        )

    def evaluate_alternatives(self, alternatives: Alternatives) -> Outcome:
        children: List[Outcome] = [self.evaluate_plan(p) for p in alternatives.children]
        statuses = [c.status for c in children]
        if Status.SUCCESS in statuses: 
            successful_indices = [i for i in range(len(children)) if children[i].status == Status.SUCCESS]
            successful_durations = [children[i].duration for i in successful_indices]
            duration = min(successful_durations)
            return Outcome(Status.SUCCESS, duration) 
        else: 
            duration = max([c.duration for c in children])
            return Outcome(Status.FAILURE, duration) 

    def evaluate_ensure(self, ensure: Ensure) -> Outcome:
        child: Outcome = self.evaluate_plan(ensure.children[0])
        duration: int = child.duration 
        success: Status = child.status 
        while not success: 
            child = self.evaluate_plan(ensure.children[0])
            duration += child.duration 
            success = success | child.status 
        return Outcome(success, duration) 
    
    def evaluate_loop(self, loop: Loop) -> Outcome:
        duration: int = 0
        for i in range(loop.max_loops):
            child: Outcome = self.evaluate_plan(loop.children[0])
            duration += child.duration 
            if child.status: 
                return Outcome(Status.SUCCESS, duration) 
        return Outcome(Status.FAILURE, duration) 
    
    def evaluate_ifelse(self, ifelse: IfElse) -> Outcome:
        test_outcome: Outcome = self.evaluate_plan(ifelse.children[0]) 
        outc: Outcome 
        if test_outcome.status: 
            outc = self.evaluate_plan(ifelse.children[1]) 
        else: 
            outc = self.evaluate_plan(ifelse.children[2]) 
        
        return Outcome(
            outc.status, 
            test_outcome.duration + outc.duration
        )
    
    def evaluate_fail(self, failure: Fail) -> Outcome:
        return Outcome(Status.FAILURE, 0)
    
    def evaluate_optional(self, opt: Optional) -> Outcome:
        outcome = self.evaluate_plan(opt) 
        return Outcome(Status.SUCCESS, outcome.duration)
