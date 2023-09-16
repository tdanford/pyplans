
from enum import Enum 

class Status(Enum): 

    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"

    def __bool__(self): 
        return self == Status.SUCCESS

    def __and__(self, other: 'Status') -> 'Status': 
        if self == Status.SUCCESS and other == Status.SUCCESS: 
            return Status.SUCCESS
        else: 
            return Status.FAILURE
    
    def __or__(self, other: 'Status') -> 'Status': 
        if self == Status.SUCCESS or other == Status.SUCCESS: 
            return Status.SUCCESS
        else: 
            return Status.FAILURE
    
    def __inv__(self) -> 'Status': 
        if self == Status.SUCCESS: 
            return Status.FAILURE
        else: 
            return Status.SUCCESS

class Outcome: 

    status: Status 
    duration: int 

    def __init__(self, status: Status, duration: int = 0): 
        self.status = status 
        self.duration = duration 
    
    def __eq__(self, other) -> bool: 
        return (
            isinstance(other, Outcome) and 
            self.status == other.status and 
            self.duration == other.duration
        )
    
    def __lt__(self, other: 'Outcome') -> bool: 
        return (self.status, self.duration) < (other.status, other.duration)

    def __hash__(self): 
        return hash((self.status, self.duration))
    
    def __repr__(self): 
        return f"{self.status}) (duration: {self.duration})"