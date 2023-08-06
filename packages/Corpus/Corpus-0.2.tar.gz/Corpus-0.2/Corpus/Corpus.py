import csv
import os
def en_vocab(word):
	main_dir = os.path.dirname(__file__)
	csv_dir = os.path.join(main_dir, 'CorpusDict.csv')
	customDict=[]
	if len(word) == 0:
		return True
	elif (word == " "):
		return True
	else:
		with open (csv_dir) as f:
			for row in csv.reader(f):
				customDict.append(row[0])
		word=word[0].lower() + word[1:]
		if word in customDict:
			return True
		else:
			word=word[0].upper() + word[1:]		
			if word in customDict:
				return True
			else:
				return False