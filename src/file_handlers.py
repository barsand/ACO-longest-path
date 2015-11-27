# file handling useful tools

def load_file(file_path):
# transform each line of data in file_path into a list of lines
	
	with open(file_path, 'r') as f: return [line.rstrip() for line in f]

def clear_file(path):
# removes all content from file at specified path, and creates
# an empty one in case it doesnt exist
	tmp = open(path, 'w')
	tmp.close

def save_list_to_file(path, content, clear=True):
	if clear: clear_file(path)
	output = open(path, 'a')
	for c in content:
		output.write(str(c))
		output.write('\n')
	output.close()
