from platypus import GeneticAlgorithm, Problem, Permutation, nondominated, unique

def ordering(x):
    # x[0] is the permutation, this calculates the difference between the permutation and an ordered list
    return sum([abs(p_i - i) for i, p_i in enumerate(x[0])])

problem = Problem(1, 1)
problem.types[0] = Permutation(range(20))
problem.function = ordering

algorithm = GeneticAlgorithm(problem)
algorithm.run(1000000)

for solution in unique(nondominated(algorithm.result)):
    print(solution.variables, solution.objectives)