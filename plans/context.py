
from typing import Dict, Iterable, Tuple

class Context: 

    """Hierarchical dictionary of values, indexed by strings, used to keep track of local information
    at each phase of the execution of a Plan
    """

    parent: 'Context' 
    env: Dict[str, any]

    def __init__(self, parent: 'Context' = None, **kwargs): 
        self.parent = parent 
        self.env = kwargs 
    
    def __getitem__(self, idx): 
        if idx in self.env: 
            return self.env[idx] 
        elif self.parent: 
            return self.parent[idx] 
        else: 
            raise KeyError(idx) 
    
    def __setitem__(self, idx: str, newvalue): 
        self.env[idx] = newvalue 
    
    def keys(self) -> Iterable[str]: 
        if self.parent: 
            for key in self.parent.keys(): 
                if key not in self.env: 
                    yield key 
        for key in self.env: 
            yield key 
    
    def key_values(self) -> Iterable[Tuple[str,any]]: 
        if self.parent: 
            for key, value in self.parent.key_values():
                if key not in self.env: 
                    yield key, value
        for key in self.env: 
            yield key, self.env[key]
    
    def as_dict(self) -> Dict[str, any]: 
        return { 
            k: v for k, v in self.key_values()
        }

