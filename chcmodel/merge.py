from os import getcwd, listdir, mkdir
from sys import argv
args = argv[1:] 
benchmarksDirectory = args[0]
modelsDirectory = args[1]
mergedFilesDirectory = args[2]
if mergedFilesDirectory not in listdir(getcwd()):
	mkdir(mergedFilesDirectory)
for benchmarkName in listdir(benchmarksDirectory):
	mergedFileContent = []
	benchmarkFile = open(benchmarksDirectory + benchmarkName, "r")
	modelFile = open(modelsDirectory + benchmarkName, "r")
	mergedFile = open(mergedFilesDirectory + "/" + benchmarkName, "w")
	for line in benchmarkFile.readlines():
		mergedFile.writelines(line)
		if line == "(check-sat)\n":
			mergedFile.writelines(modelFile.readlines())
	benchmarkFile.close()
	modelFile.close()
	mergedFile.close()