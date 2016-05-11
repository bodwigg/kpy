import requests
import json
import sys
from pprint import pprint

#strLang = "nn"
strLang = "sv"
#strLang = "no"
published = "853a2d84-5b2b-11e2-bcfd-0800200c9a66"

f = open('textMatch.txt', 'w')
nf = open('textNoMatch.txt', 'w')
bf = open('textNoRel.txt', 'w')
	

def	getMatchList(instring):
	
	#här får jag in beskrivningstexten, lterar reda på det som är intressant och läser ut det till en lista
	mReturn = []
	mstr = ""
	
	if len(instring) > 0:
		
		intI = instring.count("Jfr")
		if intI == 1:
			indI = instring.find("Jfr")
			if indI > 0:
				strC = instring[indI + 4 : len(instring)]
				#print (strC)
				if len(strC) > 0:
					mlist = strC.split(",")
					#pprint (mlist)
					for mstr in mlist:
						if len(mstr) > 0:
							#print (mstr.strip())
							mstr = mstr.strip()
							mstr = mstr.replace(".", "")
							mstr = mstr.lower()
							mReturn.append(mstr.strip())
							
	return (mReturn)
	
def matchConcept(matchlist, uuid, name):

	w1 = ""
	w2 = ""
	draftstring = ""
	if len(matchlist) > 0:
	
		for word in matchlist:
			
			#om ordet finns i matchdict
			if word in vocab:
				#word = word.encode('UTF-8')
				w = vocab[word]
				
				#blockera motlänkar så att relationen enbart skapas en väg
				blockDict[w] = True
				bf.write (w + '\n')
				
				#!!Draft%%<useruuid>%%<Källa, kommentar + ;1;
				
				w1 = w1 + ';1;' + w
				w2 = w2 + '; ' + word

			else:
				nf.write ('No match for \t' + name + ' \t'  + uuid + '\tDescription: ' + word + '\n')

	if len(w1) > 0:
		if w1[0:3] == ";1;":
			w1 = w1[3 : len(w1)]
		#else:
			#w1 = w1[0:3]
		if w2[0:2] == "; ":
			w2 = w2[2 : len(w2)]
			
		f.write (uuid + '\t' + w1 + '\t' + w2 + '\t' + name + '\n')
			
def loadMatchDict():

	matchDict = {} 
	
	mr = requests.get('http://kulturnav.org/api/list/5a145f3c-6559-44f1-8f83-119734b3e23d/0/500')
	mjson = mr.json()

	for i in mjson:
		strEntityType = i['entityType']
		
		if strEntityType == 'Concept':
			uuid = i['uuid']
			name = i['properties']['entity.name'][0]['value']['sv']
			
			matchDict[name] = uuid

	return (matchDict)
	

##############-------------------------------------------------------------------------------------------------------------

# Ladda matchningsunderlaget - hela datasetet som en dict - det förutsätter att alla termer är unika
vocab = loadMatchDict()
blockDict = {} 

iloop = 500
for c in range(-1,999, iloop):

	#här hämtar jag alla som jag Jmf i beskrivningen och som inte redan har en concept.related
	r = requests.get('http://kulturnav.org/api/search/entity.dataset_r:5a145f3c-6559-44f1-8f83-119734b3e23d,concept.related_r:!*,entity.description_sv_t:*Jfr*/'+str(c+1)+'/'+ str(c + iloop))
	rDict = r.json()

	strConceptName = ""
	strUUID = ""
	strEntityType = ""
	
	#counter = 0
	
	for i in rDict: 
		#uuid
		strUUID = i['uuid']
		
		if not strUUID in blockDict:
		
			strEntityType = i['entityType']
			
			if strEntityType == 'Concept':
				#hämta properites
				p = (i['properties'])
				
				if 'superconcept.status' in p:
					state = p['superconcept.status']
					for s in state:
						strState = s['value']
						
						#termen ska vara publicerad, inte arkiverad:
						if strState == published:
													
							#desc
							if 'entity.description' in p:
								n = p['entity.description']
								name = p['entity.name'][0]['value'][strLang]
								for e in n:
									
									if 'value' in e:
										textDesc = e['value']
										textDesc = textDesc[strLang]	
										
										a = getMatchList(textDesc)
										
										if len(a) > 0:
											b = matchConcept(a, strUUID, name )
f.close()
nf.close()
bf.close()
