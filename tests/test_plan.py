
from plans.plan import Plan, Action

def test_plan_name(): 
    p1 = Plan() 
    assert p1.plan_type == 'Plan'
    p2 = Action("Foo") 
    assert p2.plan_type == 'Action'

def test_action_equality(): 
    p1 = Action("Foo") 
    p2 = Action("Bar") 
    p3 = Action("Foo") 
    assert p1 == p1 
    assert p2 == p2 
    assert p3 == p3 
    assert p1 != p2 
    assert p2 != p3 
    assert p1 != p3 