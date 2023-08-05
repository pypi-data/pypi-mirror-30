from accrocchio.badgeofshame import accrocchio, detonator


def f(a: detonator[int]):
    pass

print(accrocchio.how_many())     # here we have 1, as you have declared a smelly parameter
print(detonator.how_many())     # here we have 1, as you have declared a smelly parameter

f(1)
print(accrocchio.how_many())     # here we still have 1
print(detonator.how_many())     # here we still have 1
