DEBUG = False

WEIGHT = 'weight'
PHEROMONE = 'pheromone'
PHEROMONE_INIT = 1
PHEROMONE_INCREASE = 3


# ITERATIONS = 15
# ANT_NUM = 20
# EVP_RATIO = 0.5

import sys
import os
import time
import random
from file_handlers import *

class ACO_Graph():

	def __init__(self, input_file_path):

		file_content = load_file(input_file_path)

		input_line1 = file_content.pop(0)
		input_line2 = file_content.pop(0)

		# parsing the input file lines into [origin, dest, weight] list
		vertices_info = [line.split() for line in file_content]

		# first line of input file holds the number of vertices
		self.num_vertices = int(input_line1)

		# second line of input file holds the origin and destination 
		# to be found in the graph
		input_line2 = input_line2.split()
		self.ORIGIN = input_line2[0]
		self.DEST = input_line2[1]

		# creating the vertices dict to be used by add_edge_vertice
		self.vertices = {}

		self.max_weight = 0

		for v in vertices_info:
			self.add_edge(v[0], v[1], int(v[2])) # specified: origin dest weight

	def create_vertex(self, index):
		if not (index in self.vertices.keys()):
			self.vertices[index] = {}

	def add_edge(self, origin, dest, weight):

		# origin = str(origin)

		if not origin in self.vertices.keys(): self.create_vertex(origin)

		self.vertices[origin][dest] = {}
		self.set_weight(origin, dest, weight)
		self.set_pheromone(origin, dest, PHEROMONE_INIT)
		if (weight > self.max_weight): self.max_weight = weight

	def get_weight(self, origin, dest): 
		return self.vertices[origin][dest][WEIGHT]

	def set_weight(self, origin, dest, weight): 
		self.vertices[origin][dest][WEIGHT] = weight

	def get_pheromone(self, origin, dest): 
		return self.vertices[origin][dest][PHEROMONE]

	def set_pheromone(self, origin, dest, pheromone): 
		self.vertices[origin][dest][PHEROMONE] = pheromone

	def get_adjacent_vertices(self, origin):
		return [ d for d in self.vertices[origin].keys() ]

	def to_string(self, print_weight=True, print_pheromone=True):

		print "\n *** PRINTING [ ",

		if print_weight: print "<weight> ",
		if print_pheromone: print "<pheromone> ",

		print "] ***\n\n",

		
		for origin in sorted( [k for k in self.vertices.keys()], key=int ):
			
			# origin = str(origin)

			print origin, "-> ",


			for dest in sorted(self.vertices[origin].keys(), key=int):
				printlist = []
				
				if print_weight:
					weight = self.get_weight(origin, dest)
					printlist.append(weight)

				if print_pheromone:
					pheromone = self.get_pheromone(origin, dest)
					printlist.append(pheromone)

				pheromone = self.get_pheromone(origin, dest)
				print dest, ":\t", printlist, "| ",

			print ""

	def is_path_simple(self, vpath):
		# i. e. a path which does not have repeating vertices
		
		tmp_vpath = sorted(vpath)

		# pigeonhole principle
		if (len(tmp_vpath) > self.num_vertices):
			print ">path has cycles"
			return False

		previous = tmp_vpath.pop(0)

		for v in tmp_vpath:
			current = v
			if (current == previous): 
				print ">path has cycles"
				return False
			previous = current

		return True

	def is_path_valid(self, vpath):

		if (len(vpath) == 0): return True

		tmp_vpath = [v for v in vpath]
		if DEBUG: print "current path: ", vpath

		if not (self.is_path_simple(vpath)):
			print "invalid path"
			return False
		
		if (len(tmp_vpath) <= 0):
			print "invalid path"
			return False

		else:
			previous = tmp_vpath.pop(0)

			for v in tmp_vpath:
				current = v

				if not (current in self.vertices[previous].keys()):
					print ">no path from ", previous, "to ", current
					print "invalid path"
					return False

				previous = current

			return True

	def fitness(self, vpath):

		if (len(vpath) == 0): return 0

		if self.is_path_valid(vpath):

			tmp_vpath = [v for v in vpath]

			total_weight = 0

			origin = tmp_vpath.pop(0)
			for dest in tmp_vpath:

				# print origin, "\t-> ", dest, "\t:\t", 8
				# print self.get_weight(origin, dest)8

				weight = self.get_weight(origin, dest)

				total_weight += weight

				origin = dest

			if DEBUG: print "total weight: ", total_weight

		else: 
			print "unable to calculate fitness"
			return None

		return total_weight

	def evaporate_pheromones(self, evp_ratio):
		
		for origin in self.vertices.keys():
			for dest in self.vertices[origin].keys():
				curr_pheromone = self.get_pheromone(origin, dest)
				self.set_pheromone(origin, dest, curr_pheromone*(1-evp_ratio))

	def smooth_things_up(self):
		# this function is responsible to make the pheromone propotional to the 
		# edges weight in order to make the random choice consider both edge's
		# weight and pheromone. after testing, maybe it should be interesting to 
		# make one or other edge attribute more important for the pick
		# due to lack of tests, it is not going to be used at this work.
		BALANCE_RATIO = 2

		max_weight = self.max_weight
		max_pheromone = 0
		
		for origin in self.vertices.keys():
			for dest in self.vertices[origin].keys():
				curr_pheromone = self.get_pheromone(origin, dest)
				if (curr_pheromone > max_pheromone):
					max_pheromone = curr_pheromone
		
		smoothing_ratio = float(max_weight) / max_pheromone
		smoothing_ratio *= BALANCE_RATIO

		print "max_weight: ", max_weight, "max_pheromone: ", max_pheromone

		for origin in self.vertices.keys():
			for dest in self.vertices[origin].keys():
				curr_pheromone = self.get_pheromone(origin, dest)
				self.set_pheromone(origin, dest, curr_pheromone*smoothing_ratio)

def ant_action(graph, ant_num):

	# print "\n** starting ant action **\n"

	origin = graph.ORIGIN
	dest = graph.DEST

	paths = []

	for i in range(ant_num):
		curr_path = generate_path(graph, origin, dest)
		if (curr_path):
			# print "appending...", curr_path
			paths.append(curr_path)

	# print "\n*** UPDATING ***\n"

	max_fitness = 0

	for path in paths: 
		
		fitness = graph.fitness(path)

		if (fitness > max_fitness):
			# print "is ", fitness, " > ", max_fitness, "?"
			return_path = [v for v in path]
			max_fitness = fitness

		origin = path.pop(0)

		for dest in path:
			pheromone = graph.get_pheromone(origin, dest)
			pheromone += PHEROMONE_INCREASE

			graph.set_pheromone(origin, dest, pheromone)

			origin = dest

			# graph.to_string()


	tmp_path = [v for v in return_path]
	
	origin = tmp_path.pop(0)
	for dest in tmp_path:

		pheromone = graph.get_pheromone(origin, dest)
		pheromone += PHEROMONE_INCREASE

		graph.set_pheromone(origin, dest, pheromone)

		origin = dest


	# print "\n** finishing ant action **\n"

	return return_path


def dict_random_weighted_pick(d):
	# based on the answer at http://stackoverflow.com/a/2570802 
	# (last checked: 2015-11-14 15:21)

    r = random.uniform(0, sum(d.itervalues()))
    s = 0.0
    for k, w in d.iteritems():
        s += w
        if r < s: return k
    return k

def generate_path(graph, origin, final_vertex):

	if DEBUG: print "** generating paths... **"

	path = [origin]


	random_vertex = origin		# so then we can enter the following while loop

	it_count = 0

	while (random_vertex != final_vertex):

		probabilities = calculate_probabilities(graph, origin)

		if DEBUG: print "*** RATIOS: ***", probabilities

		random_vertex = dict_random_weighted_pick(probabilities)

		num_tries = 0
		while random_vertex in path :
			random_vertex = dict_random_weighted_pick(probabilities)
			if DEBUG: print path, "random: ", random_vertex
			num_tries += 1
			if (num_tries > graph.num_vertices): # acceptable maximum tries
				return None


		if DEBUG: print "picked vertex: ", random_vertex
		path.append(random_vertex)

		origin = random_vertex

		it_count += 1

		if (it_count > graph.num_vertices):
			return None

	if DEBUG: print path

	if DEBUG: print "is it valid? ", graph.is_path_valid(path)

	if DEBUG: print "** ...done **"

	# print "fitness ", graph.fitness(path) ,"\tfor generated path: ", path

	return path

def calculate_probabilities(graph, curr_vertex):
	
	adjacents = graph.get_adjacent_vertices(curr_vertex)

	probabilities = {}

	if DEBUG: print "adjacents: "

	for dest in adjacents:

		curr_weight = graph.get_weight(curr_vertex, dest)
		curr_pheromone = graph.get_pheromone(curr_vertex, dest)

		if DEBUG: print dest, curr_weight, curr_pheromone

		probabilities[dest] = curr_weight * curr_pheromone

	total_values = sum( float(probabilities[d]) for d in probabilities.keys() )

	if DEBUG: print "total_values: ", total_values

	for dest in probabilities:
		probabilities[dest] /= total_values

	return probabilities

def ACO(graph, input_file_path, iterarions, ant_num, evp_ratio):

	it = 0

	max_fitness = 0
	best_path = []

	avg_fitnesses = 0

	# print "\n\niterarions:", iterarions, "\n\n"
	while (it < iterarions):

		# print "\nACO ROUND ", it

		round_result = ant_action(graph, ant_num)
		curr_fitness = graph.fitness(round_result)

		avg_fitnesses += curr_fitness

		if (curr_fitness > max_fitness):
			best_path = round_result
			max_fitness = curr_fitness

		graph.evaporate_pheromones(evp_ratio)

		# print "fitness: ", curr_fitness
		# print "best path: ", best_path

		it += 1

	avg_fitnesses /= it

	return avg_fitnesses, best_path



def main():

	if (len(sys.argv) != 5):
		print "\n** wrong usage **\n"
		sys.exit()
	

	input_file_path = sys.argv[1]
	iterarions = int(sys.argv[2])
	ant_num = int(sys.argv[3])
	evp_ratio = float(sys.argv[4])

	print "\n*****"

	print "running ACO with parameters: ", "input_file_path: ", input_file_path,
	print "iterarions: ", iterarions, "ant_num: ",
	print  ant_num, "evp_ratio: ", evp_ratio

	graph = ACO_Graph(input_file_path)

	avg_fitnesses, best_path = ACO(graph, input_file_path, iterarions, 
			ant_num, evp_ratio)

	print "\nACO RESULT: fitness (", graph.fitness(best_path), ")", best_path
	print "average round results: ", avg_fitnesses, "\n"

	# print "\ndone.\n"


if __name__ == "__main__":
    main()