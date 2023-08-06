from platypus import *

def mixed_type(x):
    print("Evaluating", x)
    return [x[0], x[1]]

problem = Problem(2, 2)
problem.types[0] = Real(0, 10)
problem.types[1] = Integer(0, 10)
problem.function = mixed_type

algorithm = NSGAII(problem, variator=CompoundOperator(SBX(), HUX(), PM(), BitFlip()))
algorithm.run(10000)

print("Final solutions:")
for solution in unique(nondominated(algorithm.result)):
    print(solution.variables, solution.objectives)