# Plans 

If you want to accomplish a goal, one thing you might do is _make a plan_.  

The `plans` package lets you write down step-by-step, or other structures of, plans -- and then lets you manipulate them, evaluate them formally, or even simulate their performance.  

Additional functions in `plans` allow you to capture _traces_ or _event histories_ of plans, and to ask questions of plans such as: 

1. What is the chance this plan fails? 
2. How long should executing this plan take? 
3. Given a partial trace of events resulting from a plan execution, how much of the plan is left to perform (and how long should it take)?  
4. Does a given trace of events correspond to an execution of a particular plan? 
5. Which of two (or more) given plans is more like to be successful, to to complete (successfully or otherwise) in a shorter amount of time? 

and a number of others. 

This is not an automation library! Nor is it intended to replicate queuing theory, formal logic, or even a programming language.  

This is just a tool to help understand plans written _by_ humans, and _for_ humans to execute.  

## Types of Plans

### Actions 

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
outcome = sample_outcome(
    Action("Feed the cat", duration=UniformRange(2, 4)
)
assert outcome.status == Status.SUCCESS
assert 2 <= outcome.duration <= 4
```

Here we have an `Outcome` object, which has two fields: `status` and `duration`.  We've already met the duration field, but `status` can take one of two values: `SUCCESS` or `FAILURE`.

Like `average_duration` above, the function `sample_outcome` takes a `Plan` as input, and produces a (random) `Outcome` for plan.    

So far our plan always succeeds, but we can make it slightly more complicated by including a _probability of success_ (and equivalently, a probability of failure).  

```python
outcome = sample_outcome( 
    Action(
        "Feed the cat", 
        success_prob=0.5, 
        duration=UniformRange(2, 4)
    )
)
assert outcome.status in ( Status.SUCCESS, Status.FAILURE ) 
```

If we only care about the probability of success, we _could_ sample a bunch of outcomes and estimate the probabilities from those, but there is also a function -- `success_probability`, that will calculate the values for us.  (Since success probabilities are modeled, at the lowest levels, as simple probabilities rather than distributions over probabilities, this can often be done analytically rather than through sampling.) 

```python
p = success_probability(
    Action(
        "Feed the cat", 
        success_prob=0.5
    )
)
assert a == 0.5 
```

So far this is pretty trivial, no more than just an accessor on a value we passed into a constructor -- but it will become more interesting when we start to consider _compound_ plans that are composed out of simpler plans.  

### Steps 

The easiest compound plan that most of us are familiar with are steps: _first_ we do something, and _then_ (if the first step is successful) we do something else.  

Imagine that, after I feed the cat, I usually get her some water.  I might write this plan, 

```python
p = Steps(
    Action("Feed the cat", success_prob=0.5, duration=3), 
    Action("Refill the cat's water", success_prob=0.5, duration=2)
)
```

(I don't know why "refilling the cat's water" would only have a 50% chance of success, but this is just an example!) 

Now, all the functions on plans we saw above produce the "right" results on this composite plan.  For example, if each step in the two-step plan has a 50% chance of success, then the overall plan has only a 25% chance of success: 

```python
assert success_probability(p) == 0.25 
``` 

since the _semantics_ of a step-based plan are that the plan only succeeds if _all_ the steps succeed (and we assume, for the moment, an independent chance of failure for each atomic `Action`).  

Similarly, the duration of the plan is the sum of the durations of the steps, 

```python
assert average_duration(p) == 5
```

because the semantics of the Steps are that each member or _child_ plan must be performed in sequence.  

Both `Steps` and `Requirements` are plans whose success are characteristic of a logical 'and' -- they only succeed when _all_ their child plans succeed.  

Are there other kinds of composite plans, that resemble a logical 'or', or any of the other connectives? 

### Options 

An `Options` plan combines a set of child plans; like `Steps` it assumes they are executed in order, serially, but unlike `Steps` the `Options` plan succeeds upon the _first success_ of its child plans.  

For example, I like buying "Cat Chow" brand cat food for my cat -- but about 20% of the time, the store doesn't have it in stock.  In those cases, I look for "Fuzzy Feline" cat food instead.  It's not as good, but it's only out of stock 5% of the time.  My plan for buying cat food then, is: 

```python
buy_plan = Options(
  Action("Buy cat chow", success_prob=0.8, duration=1), 
  Action("Buy fuzzy feline", success_prob=0.95, duration=2)
)
```

and by looking at the success probability, 

```python
assert success_probability(buy_plan) == 0.95
```

I see that I only come away from the store empty-handed 5% of the time (again, assuming that the failure rates of the two options are uncorrelated).  

### Alternatives 

Just the same way that `Requirements` generalizes `Steps` by removing the serial nature of the child plans, `Alternatives` generalizes `Options` by removing the same quality.  

An `Alternatives` plan can be executed by performing _all_ child plans in parallel, and succeeding when the _first_ child plan succeeds (or failing if they all fail).  

### Optional Plans 

### Ensure and Loop 

### Conditional Plans 

### Others 

#### `Fail` 

## Other Plan Functions

### `success_probability`

### `average_duration`

### `max_duration`

### `sample_outcome` 

### `sample_history` 

## Creating Plans

### Factory Functions 

### Parsing Plans from Text 

### Plan Libraries 
