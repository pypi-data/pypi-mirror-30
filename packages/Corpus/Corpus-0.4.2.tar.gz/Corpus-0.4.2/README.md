# Corpus
A simple English dictionary for Python

## How to use

Install Corpus using pip

```pip install Corpus```

##        
```import``` Corpus in your document

```import Corpus```

##

Use function en_vocab(string) to check whether the word is valid English word or not.

```
spell = Corpus.en_vocab
spell('word')
```

Function en_vocab will return boolean value True or False.

```True``` if the word is correct and ```False``` if not.

## Example

```
import Corpus
spell = Corpus.en_vocab
correct=[]
wrong=[]
words=['align', 'Intergalactic', 'yo-yo', 'Speling', 'javascript', 'sentenc']
for i in range(len(words)):
  if spell(words[i])==True:
    correct.append(words[i])
  else:
    wrong.append(words[i])
print "correct words are :- ", correct
print "Wrong words are :- ", wrong
print spell(words[1])
print spell(words[3])
```

Output is

```
correct words are :-  ['align', 'Intergalactic', 'yo-yo', 'javascript']
Wrong words are :-  ['Speling', 'sentenc']
True
False
```

## Current release

For Python 2.7

```Corpus version 0.4.2```

## In future

Support for definition of words, suggestions for wrong words and a lot of ```Technical terms``` will be added soon. 

