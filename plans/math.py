
from random import Random
from typing import Protocol, TypeVar, Dict

TAddable = TypeVar("TAddable") 

class Addable(Protocol): 
    def __add__(self: TAddable, other: TAddable) -> TAddable: 
        ...
    def __gt__(self: TAddable, other: TAddable) -> bool: 
        ... 
    def __ge__(self: TAddable, other: TAddable) -> bool: 
        ... 

class IntDist: 

    def sample(self, rand: Random) -> int: 
        ...
    
    def is_deterministic(self) -> bool: return False

    def max_value(self) -> int: return None

    def __add__(self: 'IntDist', other: 'IntDist') -> 'IntDist': 
        return DistributionSum(self, other) 
    
    def to_dict(self) -> Dict: 
        ...

class Constant(IntDist): 
    value: int 
    def __init__(self, v: int): 
        self.value = v 
    def is_deterministic(self) -> bool: return True
    def max_value(self) -> int: return self.value
    def sample(self, _: Random) -> int: return self.value 
    def to_dict(self) -> Dict:
        return {
            "type": "Constant", 
            "value": self.value
        }

class UniformRange(IntDist): 
    lower_value: int 
    upper_value: int 

    def __init__(self, min_value: int, max_value: int): 
        self.lower_value = min_value 
        self.upper_value = max_value 

    def max_value(self) -> int: return self.upper_value
    
    def sample(self, rand: Random) -> int: 
        return rand.randint(self.lower_value, self.upper_value) 
    
    def to_dict(self) -> Dict: 
        return {
            "type": "UniformRange", 
            "lower_value": self.lower_value, 
            "upper_value": self.upper_value
        }

class DistributionSum(IntDist): 

    left: IntDist
    right: IntDist

    def __init__(self, left: IntDist, right: IntDist): 
        self.left = left 
        self.right = right 
    
    def is_deterministic(self) -> bool:
        return self.left.is_deterministic() and self.right.is_deterministic()

    def max_value(self) -> int: 
        left_max = self.left.max_value() 
        right_max = self.right.max_value() 
        if (not left_max) or (not right_max): return None 
        return left_max + right_max 
    
    def sample(self, rand: Random) -> int: 
        return self.left.sample(rand) + self.right.sample(rand)
    
    def to_dict(self) -> Dict: 
        return {
            "type": "DistributionSum", 
            "left": self.left.to_dict(), 
            "right": self.right.to_dict()
        }

def dist_from_dict(d: Dict) -> IntDist: 
    t = d.get("type") 
    if t == 'Constant': 
        return Constant(t.get('value')) 
    elif t == 'UniformRange': 
        return UniformRange(
            t.get('lower_value'), 
            t.get('upper_value') 
        )
    elif t == 'DistributionSum': 
        return DistributionSum(
            dist_from_dict(t.get('left')), 
            dist_from_dict(t.get('right'))
        )
    else: 
        raise ValueError(t) 