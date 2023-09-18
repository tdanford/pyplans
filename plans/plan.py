
from uuid import uuid4
from typing import List, Union, TypeVar, Callable, Iterable, Dict, Generic
from random import Random 
from itertools import chain 

from rich.tree import Tree 
from rich.console import Console

from plans.outcomes import Outcome, Status
from plans.math import IntDist, Constant

def generate_id(): 
    return str(uuid4())

T = TypeVar('T')

class Evaluator(Generic[T]): 

    def evaluate_plan(self, plan: 'Plan') -> T: 
        return plan.evaluate(self) 

    def evaluate_action(self, action: 'Action') -> T: 
        ... 

    def evaluate_steps(self, steps: 'Steps') -> T:
        ... 

    def evaluate_requirements(self, reqs: 'Requirements') -> T:
        ...

    def evaluate_options(self, options: 'Options') -> T: 
        ...
    
    def evaluate_alternatives(self, alternatives: 'Alternatives') -> T: 
        ...

    def evaluate_ensure(self, ensure: 'Ensure') -> T: 
        ...
    
    def evaluate_loop(self, loop: 'Loop') -> T: 
        ...
    
    def evaluate_ifelse(self, ifelse: 'IfElse') -> T: 
        ...

    def evaluate_fail(self, failure: 'Fail') -> T: 
        ...

    def evaluate_optional(self, opt: 'Optional') -> T: 
        ...
    
    def evaluate_choices(self, choices: 'Choices') -> T: 
        ...


class Start: 

    plan: 'Plan'
    time: int 

    def __init__(self, plan: 'Plan', time: int): 
        self.plan = plan 
        self.time = time 
    
    def __eq__(self, other) -> bool: 
        return ( 
            isinstance(other, Start) and 
            (self.plan, self.time) == (other.plan, other.time)
        )
    
    def __hash__(self) -> int: return hash((self.plan, self.time))

    def __lt__(self, other: 'Start') -> bool: 
        return (self.time, self.plan.id) < (other.time, other.plan.id)

    def __gt__(self, other: 'Start') -> bool: 
        return (self.time, self.plan.id) > (other.time, other.plan.id)

class End: 

    time: int 
    status: Status 

    def __init__(self, time: int, status: Status): 
        self.time = time 
        self.status = status 

    def __eq__(self, other) -> bool: 
        return (
            isinstance(other, End) and 
            (self.time, self.status) == (other.time, other.status) 
        )
    
    def __hash__(self) -> int: 
        return hash((self.time, self.status))
    
    def __lt__(self, other: 'End') -> bool: 
        return ( 
            ( self.time, self.status)  < 
            ( other.time, other.status )
        )
    
    def __gt__(self, other: 'End') -> bool: 
        return ( 
            ( self.time, self.status)  >
            ( other.time, other.status )
        )


class Event: 

    @staticmethod 
    def complete(plan: 'Plan', start: int, end: int, status: Status) -> 'Event': 
        return Event(
            Start(plan, start), 
            End(end, status)
        )

    start: Start 
    end: End 

    def __init__(self, start: Start, end: End): 
        self.start = start 
        self.end = end 
    
    def abort(self, end_time: int) -> 'Event': 
        """Creates an equivalent event which is 'aborted' at the time 'end_time'.  

        This induces three cases: 
        1. 'end_time' is *before* this event's start time -- this is an error and 
            a ValueError will be thrown
        2. 'end_time' is *after* the event's end time -- this returns an Event which 
           is an effective *copy* of this event
        3. 'end_time' is >= this event's start time, and <= this event's end time -- 
           this returns a new Event, with the same start the current event, a new 
           end time equal to the end_time parameter, and a status of FAILURE 
        """
        if end_time < self.start.time: 
            raise ValueError(f"Can't abort an Event to a time prior to its start")
        status = self.end.status if (end_time >= self.end.time) else Status.FAILURE
        new_end = min(self.end_time, end_time) 
        return Event.complete(
            self.start.plan, 
            self.start.time, 
            new_end, 
            status
        )

    def contains_timepoint(self, time: int) -> bool: 
        return self.start_time <= time and self.end_time >= time 
    
    def overlaps_event(self, event: 'Event') -> bool: 
        return ( 
            self.contains_timepoint(event.start_time) or 
            event.overlaps_event(self.start_time)
        )
    
    def contains_event(self, event: 'Event') -> bool: 
        return ( 
            self.contains_timepoint(event.start_time) and 
            self.contains_timepoint(event.end_time)
        )
    
    @property 
    def start_time(self) -> int: return self.start.time 

    @property 
    def end_time(self) -> int: return self.end.time 

    @property 
    def plan(self) -> 'Plan': return self.start.plan 

    @property 
    def duration(self) -> int: 
        return self.end.time - self.start.time 

    @property 
    def outcome(self) -> Outcome: 
        return Outcome(
            self.end.status, 
            self.duration 
        )
    
    @property 
    def status(self) -> Status: 
        return self.end.status 

    def __eq__(self, other) -> bool: 
        return (
            isinstance(other, Event) and 
            (self.start, self.end) == (other.start, other.end) 
        )

    def __hash__(self) -> int: return hash((self.start, self.end))

    def __lt__(self, other: 'Event') -> bool: 
        return (
            (self.start, self.end) < (other.start, other.end) 
        )

class History: 

    @staticmethod 
    def with_abortable_children(self, event: Event, *histories: 'History') -> 'History': 
        abort_end = event.end_time
        evts = [e for e in chain(*[h.all_events() for h in histories])]
        should_abort = len([e for e in evts if e.end_time > abort_end]) > 0 
        if should_abort: 
            aborted = [e.abort(abort_end) for e in evts if e.start_time <= abort_end]
            aborted_event = Event.complete(
                event.plan, 
                event.start_time, 
                event.end_time, 
                Status.FAILURE
            )
            return History(
                aborted_event, *aborted
            )
        else: 
            return History(
                event, *evts
            )

    @staticmethod 
    def with_children(self, event: Event, *histories: 'History') -> 'History': 
        evts = [e for e in chain(*[h.all_events() for h in histories])]
        return History(
            event, *evts
        )

    result: Event
    events: List[Event]

    def __init__(self, result: Event, *events: Event): 
        if result is None: 
            raise ValueError("top level event in History must be non-None")
        self.result = result 
        self.events = sorted(list(events)) 
        if len(self.events) > 0: 
            if min([e.start.time for e in self.events]) < result.start.time: 
                raise ValueError(f"History contains a sub-event whose start time precedes the top-level event's start time")
            if max([e.end.time for e in self.events]) > result.end.time: 
                raise ValueError(f"History contains a sub-event whose end time exceeds the top-level event's end time")
    
    def all_events(self) -> List[Event]: 
        return self.events + [self.result] 
    
    @property 
    def start_time(self) -> int: return self.result.start.time 

    @property 
    def end_time(self) -> int: return self.result.end.time

    @property
    def sub_history(self, plan: 'Plan') -> 'History': 
        sub_plans = set(plan.descendants()) 
        top_events = sorted([x for x in self.all_events() if x.plan == plan]) 
        if len(top_events) == 0: 
            raise ValueError(f"Can't find any event in history for plan {plan}")
        latest_event = top_events[-1]
        sub_events = [x for x in self.events if x.plan in sub_plans and latest_event.contains_event(x)]
        return History(
            latest_event, 
            *sub_events
        )

    
class Plan: 

    id: str 
    name: str
    plan_type: str 
    children: List['Plan']

    def __init__(self, name: str="Plan", *children: 'Plan'): 
        self.id = generate_id()
        self.name = name
        self.plan_type = self.__class__.__name__
        self.children = list(children) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T: 
        ...
    
    def __getitem__(self, idx) -> 'Plan': 
        return self.children[idx]
    
    def __eq__(self, other) -> bool: 
        if not isinstance(other, Plan): 
            return False 
        return self.id == other.id 
    
    def __hash__(self): 
        return hash((self.id,))

    def __repr__(self): 
        return f"{self.plan_type}({self.id}, {self.name})"
    
    def descendants(self) -> Iterable['Plan']: 
        for child in self.children: 
            yield from child.descendants()
        yield self 
    
    def as_tree(self) -> Tree: 
        """Renders the Plan as a rich.Tree"""
        t: Tree = Tree(f"{self.plan_type}: {self.name}")
        for c in self.children: 
            t.add(c.as_tree())
        return t 
    
    def print_tree(self): 
        c = Console()
        c.print(self.as_tree())

P = TypeVar('P', bound=Plan) 
Factory = Callable[[], P]

def finite_loop(n: int, plan: Factory[P]) -> Plan: 
    children = [plan() for i in range(n)]
    return Options(f"Loop{n}", *children)

class Action(Plan): 
    """The simplest plan, an atomic behavior with a duration (or 
    distribution over durations) and a probability of succeess."""

    description: str 
    success_prob: float 
    duration: IntDist 

    def __init__(
        self, 
        name: str, 
        description: str = "", 
        success_prob: float = 1.0, 
        duration: Union[IntDist, int] = 0
    ): 
        Plan.__init__(self, name=name)
        self.description = description
        self.success_prob = success_prob
        self.duration = duration if isinstance(duration, IntDist) else Constant(duration) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_action(self) 
    
    def sample_outcome(self, rand: Random) -> Outcome: 
        p = rand.random() 
        d = self.duration.sample(rand) 
        return Outcome(
            Status.SUCCESS if p <= self.success_prob else Status.FAILURE, 
            d 
        )
    
class Steps(Plan):
    """Steps plans execute the child plans serially, and only suceed if all the 
    steps succeed."""

    def __init__(self, name: str, *children: Plan): 
        Plan.__init__(self, name, *children) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_steps(self)
    
    def number_steps(self): 
        for i in range(0, len(self.children)): 
            self.children[i].name = f"{i+1}. {self.children[i].name}"

class Requirements(Plan): 
    """Requirements, like a logical AND, succeed only if _all_ the child plans
    succeed.  Requirements, unlike Steps, can be performed in parallel."""

    def __init__(self, name: str, *children: Plan): 
        Plan.__init__(self, name, *children) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_requirements(self) 

class Options(Plan): 
    """Options, like a logical OR, succeed if _at least_ one of the child plans 
    succeeds.  The child plans of Options are performed serially, succeeding when 
    the first succeeds, instead of simultaneously. 
    """

    def __init__(self, name: str, *children: Plan): 
        Plan.__init__(self, name, *children) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_options(self) 

class Alternatives(Plan): 
    """Alternatives, like a logical OR, succeed if _at least_ one of the child plans 
    succeeds.  Unlike with Options, the child plans of Alternatives can be performed
    in parallel -- and the Alternatives succeed when the _first_ succeeds (and the 
    rest are aborted)
    """

    def __init__(self, name: str, *children: Plan): 
        Plan.__init__(self, name, *children) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_alternatives(self) 

class Ensure(Plan): 
    """Ensure repeats a single child plan until it is successful. 

    It's an error to use Ensure with a child plan that has a 0% chance of 
    succeed; correspondingly, Ensure always succeeds (but with an uncertain
    duration if the child's success probability is < 100%)
    """

    def __init__(self, child: Plan, name=None): 
        Plan.__init__(self, name or f"Ensure {child.plan}", child) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_ensure(self) 

class Loop(Plan): 
    """Loop repeats a single child plan until it is successful, but with at most 
    a finite number of tries.  If the plan succeeds within this number of tries, 
    then the Loop succeeds -- otherwise, if the maximum looping number is exceeded
    before the child plan succeeds, then the Loop plan fails.
    """

    max_loops: int    

    def __init__(self, child: Plan, max_loops: int, name=None): 
        Plan.__init__(self, name or f"Loop {child.plan}", child) 
        self.max_loops = max_loops
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_loop(self) 

class IfElse(Plan): 
    """IfElse has three child plans: the 'test', 'consequent', and 'alternate' 
    plans.  First, IfElse executes the 'test' plan  -- if the plan succeeds, then 
    IfElse is equivalent to the 'consequent' plan, or the 'alterate' plan if the 
    'test' plan fails."""

    def __init__(self, test: Plan, consequent: Plan, alternate: Plan, name="IfElse"): 
        Plan.__init__(self, name, test, consequent, alternate) 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_ifelse(self) 

class Fail(Plan): 
    """Fail plan *never* succeeds, and does so instantaneously"""

    def __init__(self): 
        Plan.__init__(self, "FAIL") 
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_fail(self) 

class Optional(Plan): 
    """Optional plan executes the child plan, but succeeds no matter whether the 
    child plan succeeds or fails"""

    def __init__(self, plan: Plan, name=None): 
        Plan.__init__(self, name or f"Optional {plan.name}", plan)
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_optional(self) 

class Choices(Plan): 
    """Choices plan executes exactly one of its child plans, and succeeds or fails 
    based on whether that single child plan succeeds or fails -- this is equivalent 
    to a mutually-exclusive OR, in some snese. 

    In practice, the choice that is executed is either chosen randomly or through 
    a choice function.
    """

    def __init__(self, name: str, *children: Plan): 
        Plan.__init__(self, name, *children)
    
    def evaluate(self, evaluator: Evaluator[T]) -> T:
        return evaluator.evaluate_choices(self) 

