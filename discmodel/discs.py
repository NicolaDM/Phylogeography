import ercs
import discsim
import numpy as np
import random
import math
import argparse
import newick
import phyrexxmlwriter
import beastxmlwriter
import dendropy
import treegenerator
import os

def ultrametrize(tree):
	#print(tree.as_ascii_plot())
	max_time =0
	for leaf in tree.leaf_node_iter():
		print(leaf.time)
		print(max_time)
		max_time = max(leaf.time, max_time)
	for leaf in tree.leaf_node_iter():
		leaf.edge_length = leaf.edge_length +max_time-leaf.time
		leaf.time = max_time
	return tree

parser = argparse.ArgumentParser(description='Run simulations')
parser.add_argument('-jobi', action="store", type=int, dest="job_index", default=1, help='job index')
parser.add_argument('-N', action="store", type=int, dest="num_simulations", default=1, help='number of simulations (default 1)')

args = parser.parse_args()

job_index = args.job_index
num_simulations = args.num_simulations





if not os.path.exists("output"):
	os.makedirs("output")
if not os.path.exists("output/beast"):
	os.makedirs("output/beast")
if not os.path.exists("output/beast/LV"):
	os.makedirs("output/beast/LV")    
if not os.path.exists("output/beast/LV/beast_input"):
	os.makedirs("output/beast/LV/beast_input")
if not os.path.exists("output/beast/LV/beast_output"):
	os.makedirs("output/beast/LV/beast_output")

if not os.path.exists("output/phyrex"):
	os.makedirs("output/phyrex")

if not os.path.exists("output/phyrex/LV"):
	os.makedirs("output/phyrex/LV")        
if not os.path.exists("output/phyrex/LV/phyrex_output"):
	os.makedirs("output/phyrex/LV/phyrex_output")
if not os.path.exists("output/phyrex/LV/phyrex_input"):
	os.makedirs("output/phyrex/LV/phyrex_input")
if not os.path.exists("output/root_locations"):
	os.makedirs("output/root_locations")

for index in range((job_index-1)*num_simulations, job_index*num_simulations):
	L = 100
	''' R is the diameter of the torus we are simulating on. 
	    This defines the size of the 1D or 2D space that lineages
	    can move around in.'''
	sim = discsim.Simulator(L)
	a = [None]
	n = 100
	x = np.zeros(n) 
	y = np.zeros(n) 
	for i in range(n):
		if job_index < 101:
			x[i] = (random.uniform(25, 75))%L
			y[i] = (random.uniform(25, 75))%L
			a.append((x[i], y[i]))
		else:
			x[i] = (random.uniform(45, 55))%L
			y[i] = (random.uniform(45, 55))%L
			a.append((x[i], y[i]))
	#a=[None, (0,0), (0, 1)]
	sim.sample = a
	#print(a)
	rad = 0.1    
	#lambda1 = 5000000
	#mu = L**2/(lambda1*4*math.pi*rad**4)
	#mu = L**2/(lambda1*rad**4)
	#mu= L**2/(lambda1*rad**4*math.pi*(1-(128/(45*math.pi))**2))
	mu=0.1
	lambda1=2*L**2/(mu*rad**4*math.pi)
	#print(index)
	#print("lambda = "+str(lambda1))
	sim.event_classes = [ercs.DiscEventClass(r = rad, u = mu, rate = lambda1)]
	''' All individuals within distance r of the centre of an event
	    have probability u of dying in the event 
	    and parents are thrown down uniformly within this disc.'''
	#print(sim.max_occupancy)
	
	sim.run()
	#print("max occupancy = "+str(sim.max_occupancy))
	
	pi, tau = sim.get_history()
	al = sim.get_population()[0][0]
	#print(sim.get_population())
	#file.write(str(tau[0][3])+"\n")
	#print("mu = "+str(mu))
	#print("rad = "+str(rad))

	file = open("output/root_locations/location"+str(index)+".txt", "w")
	file.write(str(al[0])+" "+str(al[1]))
	file.close()
	#print(str(pi))
	#print(str(tau))
	tree_newick = newick.convert_to_newick(pi, tau, True)
	tree = dendropy.Tree.get(data=tree_newick, schema="newick")
	#for node in tree.preorder_node_iter():
	#	if node.edge_length == None:
	#		node.edge_length = 0
	#		print("asdf")
	#		print(node.edge.length)
	tree = treegenerator.calculate_times(tree)
	tree = ultrametrize(tree)
	for leaf_index in range(1,n+1):
		leaf_label ="s"+str(leaf_index)
		if leaf_index < 10:
			leaf_label = "s000"+str(leaf_index)
		elif leaf_index < 100:
			leaf_label = "s00"+str(leaf_index)
		elif leaf_index < 1000:
			leaf_label = "s0"+str(leaf_index)	
		node = tree.find_node_with_taxon_label(leaf_label)
		node.X = a[leaf_index][0]
		node.Y = a[leaf_index][1]
		node.annotations.add_bound_attribute("X")
		node.annotations.add_bound_attribute("Y")	
		node.annotations.add_bound_attribute("time")	
	beastxmlwriter.write_BEAST_xml(tree, index, dimension=2, mcmc=10000, log_every=10, beast_input_string="output/beast/LV/beast_input/beast", beast_output_string="output/beast/LV/beast_output/beast")
	phyrexxmlwriter.write_phyrex_input(tree, index, input_string="output/phyrex/LV/phyrex_input/" , output_string="output/phyrex/LV/phyrex_output/", bound=L)
		
	#os.system('beast -overwrite -seed 123456795 "output/beast/LV/beast_input/beast'+str(index)+'.xml"') 

