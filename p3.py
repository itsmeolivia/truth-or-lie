from math import log, exp
import glob, os, re

def filenames():
    path = "bestfriend.deception.training/"
    return glob.iglob(os.path.join(path, "*"))

def tokenize(text):
    l = re.split(r'[\'\+\*\s,/\=\?\(\)\-]', text)
    result = []
    for i in xrange(0, len(l)):
        item = l[i]
        if (item != '') and '.' not in item:
            result.append(item.lower())
    return result

word_index = {} #total vocabulary
document_index = {} #arr of vocab per doc

lie_index = {}
truth_index = {}

def build_index():
  for infile in filenames():
      with open(infile) as f:
          infile = os.path.basename(infile)
          document_index[infile] = {}
          contents = f.read()
          words = tokenize(contents)
          for word in words:
              if word not in word_index:
                  word_index[word] = 0
              if word not in document_index[infile]:
                  document_index[infile][word] = 0
              word_index[word] += 1
              document_index[infile][word] += 1

              if infile[:3] == "lie":
                if word not in lie_index:
                  lie_index[word] = 0
                lie_index[word] += 1
              else:
                if word not in truth_index:
                  truth_index[word] = 0
                truth_index[word] += 1

def likelihood(doc, vocab, index): #index assumes lie or truth
  tot_like = 0.0
  for word in doc:
    likely = float(word_index[word] + 1)/(len(index) + vocab)
    tot_like += log(likely)
  #return exp(tot_like)
  return tot_like

def bayes(likely, true, false):
  return (likely * .5) / (true + false)

adjLie_index = None
adjTrue_index = None
adjVocab = None

def adjust(num):
    global adjLie_index
    global adjTrue_index
    global adjVocab

    adjLie_index = dict(lie_index)
    adjTrue_index = dict(truth_index)
    adjVocab = dict(word_index)
    if num < 98:
      name = "lie" + str(num + 1) + ".txt"
      for word in document_index[name]:
        adjLie_index[word] -= 1
        adjVocab[word] -= 1
    else:
      name = "true" + str(num - 97) + ".txt"
      for word in document_index[name]:
        adjTrue_index[word] -= 1
        adjVocab[word] -= 1

def fileName(num):
  if num < 98:
    return "lie" + str(num + 1) + ".txt"
  else:
    return "true" + str(num - 97) + ".txt"


if __name__ == "__main__":

  build_index()
  success = 0

  for i in xrange(0, 196):

    adjust(i)

    name = fileName(i)

    truth_like = likelihood(document_index[name], len(adjVocab), adjTrue_index)
    lie_like = likelihood(document_index[name], len(adjVocab), adjLie_index)

    truth = bayes(truth_like, truth_like, lie_like)
    lie = bayes(lie_like, truth_like, lie_like)

    if i < 98 and lie > truth:
      success += 1
    if i > 97 and truth > lie:
      success += 1

  print float(success)/196