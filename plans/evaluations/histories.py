from typing import List
from random import Random

from plans.plan import ( 
    Action, Fail, Optional, Steps, Plan, 
    Requirements, Options, Ensure, IfElse, Fail, 
    Event, History, Evaluator, Alternatives, Loop
)

from plans.outcomes import Status

def sample_history(p: Plan) -> History: 
    v = HistorySampler()
    value = v.evaluate_plan(p) 
    return value 

class HistorySampler(Evaluator[History]): 

    current_time: int 
    rand: Random

    def __init__(self, current_time: int = 0, rand: Random = None): 
        self.rand = rand or Random()
        self.current_time = current_time
    
    def copy(self, time: int = None) -> 'HistorySampler': 
        return HistorySampler(
            time or self.current_time, 
            self.rand 
        )

    def evaluate_action(self, action: Action) -> History:
        start_time = self.current_time
        outcome = action.sample_outcome(self.rand)
        end_time = start_time + outcome.duration
        event = Event.complete(
            action, 
            start_time,
            end_time,
            outcome.status
        )
        self.current_time = end_time 
        return History(event) 

    def evaluate_steps(self, steps: Steps) -> History:
        start_time = self.current_time
        success: Status = Status.SUCCESS
        histories: List[History] = list() 
        for child in steps.children: 
            child_history: History = self.evaluate_plan(child) 
            histories.append(child_history) 
            success = success & child_history.result.status
            self.current_time = child_history.end_time
            if not success: 
                break 
        evt = Event.complete(
            steps, 
            start_time, 
            self.current_time, 
            success
        )
        return History.with_children(
            evt, 
            *histories
        )
    
    def evaluate_requirements(self, reqs: Requirements) -> History:
        start_time = self.current_time
        n = len(reqs.children) 
        child_evaluators = [self.copy() for c in reqs.children]
        child_histories = [child_evaluators[i].evaluate_plan(reqs.children[i]) for i in range(n)]
        statuses = [h.result.status for h in child_histories]
        if Status.FAILURE in statuses: 
            first_failure = min([h.result.end_time for h in child_histories if not h.result.status])
            self.current_time = first_failure
            return History.with_abortable_children(
                Event.complete(
                    reqs, 
                    start_time, 
                    first_failure, 
                    Status.FAILURE
                ), 
                *child_histories
            )
        else: 
            max_end = max([h.result.end_time for h in child_histories])
            self.current_time = max_end
            return History.with_children(
                Event.complete(
                    reqs, 
                    start_time, 
                    max_end, 
                    Status.SUCCESS
                ), 
                *child_histories
            )

    def evaluate_options(self, options: Options) -> History:
        start_time = self.current_time
        success: Status = Status.FAILURE
        histories: List[History] = list() 
        for child in options.children: 
            child_history: History = self.evaluate_plan(child) 
            histories.append(child_history) 
            success = success | child_history.result.status
            self.current_time = child_history.end_time
            if success: 
                break 
        evt = Event.complete(
            options, 
            start_time, 
            self.current_time, 
            success
        )
        return History.with_children(
            evt, 
            *histories
        )

    def evaluate_alternatives(self, alts: Alternatives) -> History:
        start_time = self.current_time
        n = len(alts.children) 
        child_evaluators = [self.copy() for c in alts.children]
        child_histories = [child_evaluators[i].evaluate_plan(alts.children[i]) for i in range(n)]
        statuses = [h.result.status for h in child_histories]
        if Status.SUCCESS in statuses: 
            first_success = min([h.result.end_time for h in child_histories if h.result.status])
            self.current_time = first_success
            return History.with_abortable_children(
                Event.complete(
                    alts, 
                    start_time, 
                    first_success, 
                    Status.SUCCESS
                ), 
                *child_histories
            )
        else: 
            max_end = max([h.result.end_time for h in child_histories])
            self.current_time = max_end
            return History.with_children(
                Event.complete(
                    alts, 
                    start_time, 
                    max_end, 
                    Status.FAILURE
                ), 
                *child_histories
            )

    def evaluate_ensure(self, ensure: Ensure) -> History:
        start_time = self.current_time 
        histories: List[History] = list() 
        child: History = self.evaluate_plan(ensure.children[0])
        histories.append(child) 
        success: Status = child.result.status 
        while not success: 
            child = self.evaluate_plan(ensure.children[0])
            histories.append(child) 
            success = success | child.result.status 
            self.current_time = child.result.end_time
        evt = Event.complete(
            ensure, 
            start_time, 
            self.current_time, 
            success 
        )
        return History.with_children(
            evt, *histories
        )

    def evaluate_loop(self, loop: Loop) -> History:
        start_time = self.current_time 
        histories: List[History] = list() 
        for i in range(loop.max_loops): 
            child: History = self.evaluate_plan(loop.children[0])
            histories.append(child) 
            self.current_time = child.result.end_time
            if child.result.status: 
                evt = Event.complete(
                    loop, 
                    start_time, 
                    self.current_time, 
                    Status.SUCCESS 
                )
                return History.with_children(
                    evt, *histories
                )
        evt = Event.complete(
            loop, 
            start_time, 
            self.current_time, 
            Status.FAILURE 
        )
        return History.with_children(
            evt, *histories
        )
    
    
    def evaluate_ifelse(self, ifelse: IfElse) -> History:
        start_time = self.current_time
        test_history: History = self.evaluate_plan(ifelse.children[0]) 
        outc: History = None
        if test_history.result.status: 
            outc = self.evaluate_plan(ifelse.children[1]) 
        else: 
            outc = self.evaluate_plan(ifelse.children[2]) 

        evt = Event.complete(
            ifelse, 
            start_time, 
            self.current_time, 
            outc.result.status
        )
        return History.with_children(
            evt, 
            test_history, outc 
        )
    
    def evaluate_fail(self, failure: Fail) -> History:
        return History(
            Event.complete(
                failure, self.current_time, self.current_time, Status.FAILURE
            )
        )
    
    def evaluate_optional(self, opt: Optional) -> History:
        inner_history = self.evaluate_plan(opt) 
        evt = Event.complete(
            opt, 
            inner_history.start_time, 
            inner_history.end_time, 
            Status.SUCCESS
        )
        return History.with_children(evt, inner_history) 

