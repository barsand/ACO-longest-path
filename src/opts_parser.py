import argparse

def opts_parser():
	
	parser = argparse.ArgumentParser(description="""Processes IP alias list and
			assigns a pair of coordinates according to several IP Geolocation
			services using their APIs.""")

	requiredNamed = parser.add_argument_group('required arguments')
	requiredNamed.add_argument('-i', metavar='INPUT', nargs='+', 
			help='input file(s)', required=True)
	requiredNamed.add_argument('-o', metavar='PFX', 
			help='output files prefix',	required=True)
	requiredNamed.add_argument('-x', metavar='.EXTENSION', 
			help='output file extension',	required=True)


	args = parser.parse_args()

	return (args.i, args.o, args.x)