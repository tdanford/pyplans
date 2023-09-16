
from plans.outcomes import Outcome, Status 

def test_status_boolean_values(): 
    assert Status.SUCCESS
    assert not Status.FAILURE 
    assert Status.SUCCESS & Status.SUCCESS
    assert not (Status.SUCCESS & Status.FAILURE)
    assert Status.SUCCESS | Status.FAILURE
    assert Status.FAILURE | Status.SUCCESS
    assert not (Status.FAILURE | Status.FAILURE)

def test_status_in_list(): 
    assert Status.SUCCESS in [Status.FAILURE, Status.SUCCESS, Status.FAILURE]
    assert Status.SUCCESS not in [Status.FAILURE, Status.FAILURE]

def test_outcome_equality(): 
    o1 = Outcome(Status.SUCCESS, 1) 
    o2 = Outcome(Status.SUCCESS, 1) 
    o3 = Outcome(Status.FAILURE, 1) 
    o4 = Outcome(Status.SUCCESS, 2) 

    assert o1 == o1 
    assert o1 == o2 
    assert o1 != o3 
    assert o1 != o4 