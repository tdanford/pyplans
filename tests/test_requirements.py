from plans import Requirements, Action, success_probability, average_duration

def test_simple_requirements(): 
    r = Requirements(
            "b", 
            Action("D", duration=3, success_prob=0.9), 
            Action("E", duration=2, success_prob=0.5) 
        )
    assert success_probability(r) == 0.45
    assert abs(average_duration(r, n=1000) - 2.5) <= 0.1



