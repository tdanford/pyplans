
from typing import TypeVar, Generic

T = TypeVar("T") 

class Event(Generic[T]): 

    start: int 
    end: int
    data: T 

    def __init__(self, start: int, end: int, data: T = None): 
        if end < start: raise ValueError("start must be <= end")
        self.start = start 
        self.end = end 
        self.data = data 
    
    @property 
    def duration(self) -> int: return self.end - self.start 

    @property 
    def is_instantaneous(self) -> bool: return self.start == self.end 

    def shift(self, t: int) -> 'Event[T]': 
        return Event(self.start + t, self.end + t, self.data)
    
    def scale(self, f: float) ->'Event[T]': 
        ns: int = round(f * self.start)
        ne: int = round(f * self.end) 
        return Event(ns, ne, self.data) 

    def contains_time(self, t: int) -> bool: 
        return self.start <= t and self.end >= t 

    def overlaps(self, other: 'Event') -> bool: 
        return self.contains_time(other.start) or other.contains_time(self.start) 
    
    def contains(self, event: 'Event') -> bool: 
        return self.start <= event.start and self.end >= event.end 

    def precedes(self, event: 'Event') -> bool: 
        return self.end < event.start
    
    def precedes_time(self, t: int) -> bool: 
        return self.end < t 

    def follows(self, event: 'Event') -> bool: 
        return event.precedes(self) 
    
    def follows_time(self, t: int) -> bool: 
        return self.start > t 

    def __lt__(self, other: 'Event') -> bool:
        return (self.start, self.end) < (other.start, other.end) 

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Event) and 
            self.start == other.start and 
            self.end == other.end and 
            self.data == other.data 
        )
    
    def __hash__(self) -> int: return hash((self.start, self.end, self.data))

    def __repr__(self) -> str: 
        if self.data: 
            return f"({self.start}, {self.end} : {self.data})"
        else: 
            return f"({self.start}, {self.end})"
    
