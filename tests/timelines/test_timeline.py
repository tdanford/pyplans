
from plans.timelines import Timeline, Event

def test_timeline_holds_events(): 
    t = Timeline() 
    assert len(t.events) == 0 
    t.add_event(Event(1, 2)) 
    assert len(t.events) == 1 
    t.add_event(Event(1, 2))
    assert len(t.events) == 2 
    t.add_event(Event(3, 4)) 
    assert len(t.events) == 3 