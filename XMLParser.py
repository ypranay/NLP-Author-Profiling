import os
from bs4 import  BeautifulSoup
import json
import nltk
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize,word_tokenize

fp = open('blogdata.json','w')
BASE_DIR = "/home/wayne/Documents/blogs"
    
def extract_entity_names(tree):
    entity_names = []
    if hasattr(tree, 'label') and tree.label:
    	if tree.label() == 'NE':
    		entity_names.append(' '.join([child[0] for child in tree]))
    	else:
    		for child in tree:
    			entity_names.extend(extract_entity_names(child))
    return entity_names

def computeFeatures(post):
	numHTMLLinks = post.count("urlLink")
	post = post.replace('urlLink','')
	sentences = nltk.sent_tokenize(post)
	tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
	tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
	chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
	avg_sentlen = float(sum([len(word_tokenize(a)) for a in sentences]))/len(sentences)  
	numUniqueWords = len(set(word_tokenize(post)))
	named_entities = []
	for chunk in chunked_sentences:
		entities = sorted(list(set([word for tree in chunk for word in extract_entity_names(tree)])))
		for e in entities:
			if e not in named_entities:
				named_entities.append(e)
	print(named_entities)
	return numHTMLLinks,avg_sentlen,len(named_entities),numUniqueWords

def parseXMLToBloggerInfoDict(path):
    blogger_dict = {}
    blogger_id,gender,age,industry, sign = path.split(os.path.sep)[-1].split(".xml")[0].split(".")
    blogger_dict["ID"] = blogger_id
    blogger_dict["Sex"] = gender
    blogger_dict["Age"] = int(age)
    blogger_dict["Dates"] = []
    blogger_dict["Posts"] = []
    s = file(path,"r").read().replace("&nbsp;", " ")
    s = s.replace("<Blog>", "").replace("</Blog>", "").strip()
    HTMLLinksPerFile,SenLength,ProperNouns,UniqueWords,count= 0,0,0,0,0
    for e in s.split("<date>")[1:]:
    	count += 1
        date_and_post = e.split("</date>")
        blogger_dict["Dates"].append(date_and_post[0].strip())
        post = date_and_post[1].replace("<post>","").replace("</post>","").strip()
        post = BeautifulSoup(post).get_text()
    	numHTMLLinks, average_sentencelen, numPropernouns, numUniqueWords = computeFeatures(post)
        HTMLLinksPerFile += numHTMLLinks
        SenLength += average_sentencelen
        ProperNouns += numPropernouns
        UniqueWords += numUniqueWords
        blogger_dict["Posts"].append(post)
    
    average_HTMLLinks = float(HTMLLinksPerFile)/count
    average_SenLength = float(SenLength)/count
    average_ProperNouns = float(ProperNouns)/count
    average_UniqueWords = float(UniqueWords)/count
    print("Avg HTML Links = %.4f\nAvg Sentence Length = %.4f\nAvg Proper Nouns = %.4f\nAvg Unique Words = %.4f"%(average_HTMLLinks,average_SenLength,average_ProperNouns,average_UniqueWords))
    json.dump(blogger_dict,fp, indent=4)

#xmlfile = '5114.male.25.indUnk.Scorpio.xml'
for xmlfile in os.listdir(BASE_DIR):
	parseXMLToBloggerInfoDict("%s%s%s" % (BASE_DIR, os.path.sep, xmlfile))


        