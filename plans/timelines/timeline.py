
from typing import List, Dict, Iterable, TypeVar
from rich.console import Console 
from io import StringIO

from .event import Event 

class Timeline: 

    events: List[Event]

    def __init__(self, events: Iterable[Event] = None): 
        self.events = sorted(list(events or [])) 
    
    def add_event(self, event: Event): 
        self.events.append(event) 
        self.events.sort() 

T = TypeVar("T")

class Window: 

    """A Window maps a region in time-space (t1, t2) into a region in some spatial dimension (x1, x2) 
    """

    t1: int 
    t2: int 
    x1: int 
    x2: int
    time_to_space: float

    def __init__(self, t1: int, t2: int, x1: int, x2: int): 
        if t2 <= t1: 
            raise ValueError("Cannot Window a 0 or negative-width time interval")
        if x2 < x1: 
            raise ValueError("Cannot map to a negative-width space interval")
        self.t1 = t1 
        self.t2 = t2 
        self.x1 = x1 
        self.x2 = x2 
        self.time_to_space = (x2 - x1) / (t2 - t1) 

    def map_event(self, event: Event[T]) -> Event[Event[T]]: 
        return Event(
            event.start - self.t1, 
            event.end - self.t1, 
            event
        ).scale(self.time_to_space).shift(self.x1)
    
    @property 
    def target_width(self) -> int: 
        return self.x2 - self.x1 

class StringBuffer: 

    len: int 
    buffer: List[str]    

    def __init__(self, len: int): 
        self.len = len 
        self.buffer = [' ' for i in range(len)]
    
    def setchar(self, i: int, v: str): 
        if len(v) > 1: raise ValueError()
        self.buffer[i] = v 
    
    def getvalue(self) -> str: 
        b = StringIO() 
        for e in self.buffer: 
            b.write(e) 
        return b.getvalue()
    
    def __setitem__(self, idx, newvalue): 
       self.setchar(idx, newvalue) 
    
    def __add__(self, other: 'StringBuffer') -> 'StringBuffer': 
        b2 = self.duplicate() 
        b2.layer_on(other) 
        return b2 
    
    def duplicate(self) -> 'StringBuffer':
        b = StringBuffer(self.len) 
        for i in range(self.len): 
            b.buffer[i] = self.buffer[i]
        return b
    
    def layer_on(self, layer: 'StringBuffer'): 
        for i in range(min(layer.len, self.len)): 
            if layer.buffer[i] != ' ': 
                self.buffer[i] = layer.buffer[i]


class TrackedTimeline: 

    """TrackedTimeline associates a Timeline with a Window -- using these two inputs, every 
    event in the Timeline is mapped to a distinct track, such that no two Events overlap 
    in the 'target space' of the Window.  
    """

    timeline: Timeline 
    windowed_events: List[Event]
    window: Window
    tracks: int 
    event_tracks: Dict[Event, int] 
    track_events: Dict[int, List[Event]]

    def __init__(self, timeline:Timeline, window: Window): 
        self.window = window
        self.timeline = timeline 
        self.windowed_events = [window.map_event(e) for e in self.timeline.events]
        self._do_layout()
    
    def _do_layout(self): 
        self.event_tracks = {} 
        self.track_events = {}
        self.tracks = 0 

        for event in self.timeline.events: 
            event_track = 0
            while event_track < self.tracks and self.track_events[event_track][-1].overlaps(event): 
                event_track += 1
            if event_track > self.tracks: 
                self.tracks = event_track 
                self.track_events[event_track] = [] 
            self.track_events[event_track].append(event) 
            self.event_tracks[event] = event_track 
    
    def _render_event(self,event: Event, buffer:StringBuffer): 
        for i in range(event.start, event.end+1): 
            buffer[i] = '-'
    
    def _render(self) -> Iterable[str]: 
        for i in range(self.tracks-1, -1, -1): 
            b = StringBuffer(self.window.target_width)
            for e in self.track_events[i]: 
                self._render_event(e, b)
    
    def display(self, console: Console):
        for line in self._render(): 
            console.print(line)
    
    def as_string(self) -> str: 
        return '\n'.join(self._render())

