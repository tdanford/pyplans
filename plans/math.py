
from random import Random
from typing import Protocol, TypeVar 

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

    def __add__(self: 'IntDist', other: 'IntDist') -> 'IntDist': 
        return DistributionSum(self, other) 

class Constant(IntDist): 
    value: int 
    def __init__(self, v: int): 
        self.value = v 
    def sample(self, _: Random) -> int: return self.value 

class UniformRange(IntDist): 
    min_value: int 
    max_value: int 

    def __init__(self, min_value: int, max_value: int): 
        self.min_value = min_value 
        self.max_value = max_value 
    
    def sample(self, rand: Random) -> int: 
        return rand.randint(self.min_value, self.max_value) 

class DistributionSum(IntDist): 

    left: IntDist
    right: IntDist

    def __init__(self, left: IntDist, right: IntDist): 
        self.left = left 
        self.right = right 
    
    def sample(self, rand: Random) -> int: 
        return self.left.sample(rand) + self.right.sample(rand)