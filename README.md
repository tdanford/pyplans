# Plans 

If you want to accomplish a goal, one thing you might do is _make a plan_.  

## Actions 

The simplest possible plan might be: take an action. 

For example, I have a cat and I need to feed her regularly.  Imagine that it usually takes me three minutes to feed this hungry kitten.  

```python
a = Action("Feed the cat", duration=3) 
assert average_duration(a) == 3 
```

The `Action` class is a subclass of `Plan`, and `average_duration` is a function that takes a `Plan` and returns the average time required to execute that plan.  

(Note: there are no units attached to the duration here, duration values for now are just taken as unit-less integers.) 

The duration of this action, so far, is constant -- but this is probably unrealistic.  Sometimes I have the cat food right at hand and filling the cat's bowl is quicker; but sometimes I have to retrieve another bag's supply of cat food from my cupboard first.  

To model this uncertainty in the duration of an action, we can substitute a _distribution_ over durations for the constant `3`.  For example, let's imagine that feeding the cat takes either 2, 3, or 4 minutes with equal probability.  

We can write, 

```python
a = Action("Feed the cat", duration=UniformRange(2,4))
assert abs(average_duration(a, n=1000) - 3.0) <= 0.1
```
Now it becomes clear that `average_duration` is actually _sampling_ -- here we tell it to sample 1000 durations, and report the mean across all durations, checking that it's "close" to the same mean value, 3.0

Plans don't just take time; they can also succeed or fail.  So far, we've modeled 'feeding the cat' as an action -- a simple, atomic plan -- that _always succeeds_ with probabiity 100%.  To see this, we can sample an _outcome_ for a plan: 

```python
a = Action("Feed the cat", duration=UniformRange(2, 4)) 
outcome = sample_outcome(a) 
assert outcome.status == Status.SUCCESS
assert 2 <= outcome.duration <= 4
```

Here we have an `Outcome` object, which has two fields: `status` and `duration`.  We've already met the duration field, but `status` can take one of two values: `SUCCESS` or `FAILURE`.  

So far our plan always succeeds, but we can make it slightly more complicated by including a _probability of success_ (and equivalently, a probability of failure).  

```python
a = Action("Feed the cat", success_prob=0.5, duration=UniformRange(2, 4)) 
outcome = sample_outcome(a) 
assert outcome.status in ( Status.SUCCESS, Status.FAILURE ) 
```

