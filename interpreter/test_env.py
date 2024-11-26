from env_v4 import EnvironmentManager
import copy

env1 = EnvironmentManager()
env2 = EnvironmentManager()

shallow_copy = copy.copy(env1)
normal_copy = env2
env1.push_func()
env2.push_func()

env1.push_block()
env2.push_block()

env1.create("x", 9)
env2.create("x", 9)

print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")

env1.push_block()
env1.create("y", 10)

env2.push_block()
env2.create("y", 10)

print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")

shallow_copy.create("z", 11)
normal_copy.create("z", 11)

print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")

shallow_copy.pop_block()
normal_copy.pop_block()

print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")


(shallow_copy.environment[0][1]) = 10
(normal_copy.environment[0][1]) = 10

print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")


env1.environment = [{"z": 42}]
env2.environment = [{"z": 42}]

print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")

normal_copy.environment = [{"z": 43}]
shallow_copy =  copy.copy(env1)
print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")

new_list = []
shallow_copy.environment = new_list
normal_copy.environment = []
print(f"Environment 1: {env1.environment}, Environment 2: {env2.environment}") 
print(f"Shallow Copy: {shallow_copy.environment}, Normal Copy: {normal_copy.environment}")

