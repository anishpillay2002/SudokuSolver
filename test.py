from itertools import product
temp = []
temp.append([1,2,3,4])
temp.append([5,6,7,8,9])
temp.append([10,11,12])               # so a=['1', '2', '3', '4']
# print(list(product(*temp)))
b = [1,231,51,2,1]

a  = lambda x: x[0] == x[2]
c = a(b)
d=1