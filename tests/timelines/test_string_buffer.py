
from plans.timelines.timeline import StringBuffer

def test_buffer_set_item(): 
    b = StringBuffer(5) 
    b[1] = '*' 
    assert b.getvalue() == ' *   '
    b[2] = '-' 
    b[1] = '-' 
    assert b.getvalue() == ' --  '

def test_buffer_layering(): 
    b = StringBuffer(5) 
    for i in range(b.len): b[i] = str(i) 
    assert b.getvalue() == '01234'

    b2 = StringBuffer(5) 
    b2[1] = '-' 

    b.layer_on(b2) 
    assert b2.getvalue() == ' -   '
    assert b.getvalue() == '0-234'

def test_buffer_adding(): 
    b = StringBuffer(5) 
    for i in range(b.len): b[i] = str(i) 
    assert b.getvalue() == '01234'

    b2 = StringBuffer(5) 
    b2[1] = '-' 

    b3 = b + b2
    assert b.getvalue() == '01234'
    assert b2.getvalue() == ' -   '
    assert b3.getvalue() == '0-234'
