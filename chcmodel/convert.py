from os import getcwd, listdir, mkdir
from sys import argv
args = argv[1:]
modelsDirectory = args[1]
if modelsDirectory not in listdir(getcwd()):
	mkdir(modelsDirectory)
outputDirectory = args[0]
output = listdir(outputDirectory)
for out in output:
	content = listdir(outputDirectory + "/" + out)
	modelName = content[0] if content[0][-3:] == "txt" else content[1]
	with open(outputDirectory + "/" + out + "/" + modelName, "r") as f_:
		model = f_.readlines()[2:-2]
	newModel = []
	for line in model:
		line = ' '.join(line.split()[1:]) + '\n'
		newModel.append(line)
	with open(modelsDirectory + "/" + out, "w") as f_:
		f_.writelines(newModel)
