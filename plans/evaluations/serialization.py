
import json 
from functools import reduce
from typing import List, Dict
from plans.plan import Action, Alternatives, Fail, Loop, Optional, Steps, Plan, Requirements, Options, Ensure, IfElse, Fail, Evaluator
from plans.math import dist_from_dict

def serialize(plan: Plan) -> str: 
    return json.dumps(DictTranslator().evaluate_plan(plan))

def deserialize(ser: str) -> Plan: 
    serialized: Dict = json.loads(ser) 
    return from_dict(serialized)

def from_dict(d: Dict) -> Plan: 
    t = d.get('type')
    children = [from_dict(dc) for dc in d.get('children', [])]
    if t == 'Action': 
        return Action(
            d.get('name'), 
            d.get('description'), 
            d.get('success_prob'), 
            dist_from_dict(d.get('duration')) 
        )
    elif t == 'Steps': 
        return Steps(t.get('name'), *children) 
    elif t == 'Requirements': 
        return Requirements(t.get('name'), *children) 
    elif t == 'Options': 
        return Options(t.get('name'), *children) 
    elif t == 'Alternatives': 
        return Alternatives(t.get('name'), *children)
    elif t == 'Ensure': 
        return Ensure(children[0], name=t.get('name'))
    elif t == 'Loop': 
        return Loop(children[0], t.get('max_loops'), name=t.get('name')) 
    elif t == 'Optional': 
        return Optional(children[0], name=t.get('name')) 
    elif t == 'Fail': 
        return Fail() 
    elif t == 'IfElse': 
        return IfElse(
            children[0], 
            children[1], 
            children[2], 
            name=t.get('name')
        )

class DictTranslator(Evaluator[Dict]): 

    def evaluate_action(self, action: Action) -> Dict:
        return {
            "type": "Action", 
            "name": action.name, 
            "description": action.description, 
            "success_prob": action.success_prob, 
            "duration": action.duration.to_dict()
        }

    def generic_plan_dict(self, plan: Plan, type: str) -> Dict: 
        children: List[Dict] = [self.evaluate_plan(p) for p in plan.children]
        return {
            "type": type, 
            "name": plan.name, 
            "children": children
        }

    def evaluate_steps(self, steps: Steps) -> Dict:
        return self.generic_plan_dict(steps, "Steps")
    
    def evaluate_requirements(self, reqs: Requirements) -> Dict:
        return self.generic_plan_dict(reqs, "Requirements")
    
    def evaluate_options(self, options: Options) -> Dict:
        return self.generic_plan_dict(options, "Options")

    def evaluate_alternatives(self, alternatives: Alternatives) -> Dict:
        return self.generic_plan_dict(alternatives, "Alternatives")

    def evaluate_ensure(self, ensure: Ensure) -> Dict:
        return self.generic_plan_dict(ensure, "Ensure")
    
    def evaluate_loop(self, loop: Loop) -> Dict:
        loop_dict = self.generic_plan_dict(loop, "Loop")
        loop_dict['max_loops'] = loop.max_loops
        return loop_dict 
    
    def evaluate_optional(self, opt: Optional) -> Dict:
        return self.generic_plan_dict(opt, "Optional")
    
    def evaluate_fail(self, failure: Fail) -> Dict:
        return {
            "type": "Fail"
        }
    
    def evaluate_ifelse(self, ifelse: IfElse) -> Dict: 
        return self.generic_plan_dict(ifelse, "IfElse")
    