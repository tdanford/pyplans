
from plans import * 
from plans.math import * 
from plans.outcomes import Status, Outcome

def close_to(value, target, eps=0.01) -> bool: 
    return abs(value - target) <= eps

def test_example1(): 
    a = Action("Feed the cat", duration=3) 
    assert average_duration(a) == 3 

def test_example2(): 
    a = Action("Feed the cat", duration=UniformRange(2,4))
    assert abs(average_duration(a, n=1000) - 3.0) <= 0.1

def test_example3(): 
    a = Action("Feed the cat", duration=UniformRange(2, 4)) 
    outcome = sample_outcome(a) 
    assert outcome.status == Status.SUCCESS
    assert 2 <= outcome.duration <= 4

def test_example4(): 
    a = Action("Feed the cat", success_prob=0.5, duration=UniformRange(2, 4)) 
    outcome = sample_outcome(a) 
    assert outcome.status in ( Status.SUCCESS, Status.FAILURE ) 

def test_example5(): 
    a = Action("Feed the cat", success_prob=0.5, duration=UniformRange(2, 4)) 
    outcomes = [sample_outcome(a) for i in range(100)]
    assert len([o for o in outcomes if o.status == Status.SUCCESS]) > 0
    assert len([o for o in outcomes if o.status == Status.FAILURE]) > 0

def test_example6(): 
    a = Action("Feed the cat", success_prob=0.5, duration=UniformRange(2, 4)) 
    assert success_probability(a) == 0.5

def test_example7(): 
    s = Steps(
        "Feed the cat", 
        Action("Get the cat food", duration=1), 
        Action("Fill the cat food bowl", duration=3) 
    )
    assert average_duration(s) == 4

def test_example8(): 
    s = Steps(
        "Feed the cat", 
        Action("Get the cat food", duration=1, success_prob=0.5), 
        Action("Fill the cat food bowl", duration=3, success_prob=0.5) 
    )
    assert success_probability(s) == 0.25

def test_example9(): 
    s = Steps(
        "Feed the cat", 
        Action("Get the cat food", duration=1, success_prob=0.5), 
        Action("Fill the cat food bowl", duration=3, success_prob=0.5) 
    )
    assert abs(average_duration(s, n=1000) - 2.5) <= 0.1

def test_example10(): 
    s = Steps("Taking care of the cat",
            Steps(
                "Feed the cat", 
                Action("Get the cat food", duration=1, success_prob=0.5), 
                Action("Fill the cat food bowl", duration=3, success_prob=0.5) 
            ), 
            Action("Clean the litter box", success_prob=0.8, duration=1)
    )
    assert success_probability(s) == 0.2

