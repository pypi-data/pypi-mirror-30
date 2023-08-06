"""
inheritance script, by Denver

SCRIPT IS WIP
r001: 20180321-0131 (CORE CODE WORKS!)
"""

from dbi.dbi import dbi # import dbi for debugging
db = {'debug_active': True, 'verbosity_level': 2} # dictionary for dbi
dbi(db,3,"Successfully imported dbi!") # test dbi import

# define the person class
class Person:
    """
    Test gene inheritance based on different trait activation properties (e.g. linked to x chromosome)
    """
    def __init__(self,name,gender,chromosomes):
        self.name = name
        self.gender = gender
        self.chromosomes = chromosomes
        # bool for whether the first chromatid has an active or inactive version of the allele which causes the phenotype
        #self.chromatid1 = chromatid1
        #self.chromatid2 = chromatid2
    def testFor(self,trait):
        if (trait.sexLinked == False): #TEST IF LINKED TO X OR Y, THEN TEST IF DOMINANT, RETURN IF PHENOTYPE IS ACTIVE
            if (trait.dominant):
                if (self.chromosomes[trait.name]['cTid1']) or (self.chromosomes[trait.name]['cTid2']):
                    return True
                else:
                    return False
            else:
                if (not self.chromosomes[trait.name]['cTid1']) and (not self.chromosomes[trait.name]['cTid2']):
                    return True
                else:
                    return False
        elif (trait.sexLinked == 'x'):
            if (self.gender == 'male'):
                if (self.chromosomes[trait.name]['cTid1']):
                    return True
                else:
                    return False
            elif (self.gender == 'female'):
                if (trait.dominant):
                    if (self.chromosomes[trait.name]['cTid1']) or (self.chromosomes[trait.name]['cTid2']):
                        return True
                    else:
                        return False
                else:
                    if (not self.chromosomes[trait.name]['cTid1']) and (not self.chromosomes[trait.name]['cTid2']):
                        return True
                    else:
                        return False
            else:
                print("Error: Gender invalid (this isn't Tumblr)")
        elif (trait.sexLinked == 'y'):
            if (self.gender == 'male'):
                if (trait.dominant):
                    if (self.chromosomes[trait.name]['cTid2']):
                        return True
                    else:
                        return False
                else:
                    if (not self.chromatid2):
                        return True
                    else:
                        return False
            elif (self.gender == 'female'):
                #Females cannot have an x-linked trait
                return False
            else:
                print("Error: Gender invalid (this isn't Tumblr)")
        else:
            print("ERROR: sexLinked is an invalid input")
    def calcGenotype(self,allele):
        chromatid1type = 'X'

        if (self.gender == 'male'):
            chromatid2type = 'Y'
        elif (self.gender == 'female'):
            chromatid2type = 'X'

        if (self.chromatid1):
            chromatid1power = allele.upper()
        else:
            chromatid1power = allele.lower()

        if (self.chromatid2):
            chromatid2power = allele.upper()
        else:
            chromatid2power = allele.lower()

        output = chromatid1type + chromatid1power + " " + chromatid2type + chromatid2power

        return output

class Phenotype:
    """
    Specify whether a trait is sexlinked or not (if so where) and whether it is dominant
    """
    def __init__(self,**kwargs):
        if 'name' in kwargs: self.name = kwargs['name']
        else: raise Exception("information in Phenotype class not specified")
        if 'sexLinked' in kwargs:
            if (kwargs['sexLinked'] is 'y' or 'x' or False):
                self.sexLinked = kwargs['sexLinked']
            else: raise Exception("sexLinked must be either 'male', 'female' or False")
        if 'dominant' in kwargs: self.dominant = kwargs['dominant']
        if 'allele' in kwargs: self.allele = kwargs['allele']

#script body
people = [
    Person(
        "John","male",chromosomes = {
            'haemophilia': {'trait': 'haemophilia','cTid1': True,'cTid2': False},
            'brownEyes': {'trait': 'brownEyes','cTid1': True,'cTid2': False},
            'maleInfertility': {'trait': 'maleInfertility','cTid1': True,'cTid2': False}
        }
    ),
    Person(
        "Jill","female",chromosomes = {
            'haemophilia': {'trait': 'haemophilia','cTid1': False,'cTid2': True},
            'brownEyes': {'trait': 'brownEyes','cTid1': False,'cTid2': True},
            'maleInfertility': {'trait': 'maleInfertility','cTid1': False,'cTid2': True}
        }
    ),
    Person(
        "Theodore","male",chromosomes = {
            'haemophilia': {'trait': 'haemophilia','cTid1': False,'cTid2': True},
            'brownEyes': {'trait': 'brownEyes','cTid1': False,'cTid2': True},
            'maleInfertility': {'trait': 'maleInfertility','cTid1': False,'cTid2': True}
        }
    ),
    Person(
        "Kanwal","male",chromosomes = {
            'haemophilia': {'trait': 'haemophilia','cTid1': True,'cTid2': True},
            'brownEyes': {'trait': 'brownEyes','cTid1': True,'cTid2': True},
            'maleInfertility': {'trait': 'maleInfertility','cTid1': True,'cTid2': True}
        }
    ),
    Person(
        "Peter","male",chromosomes = {
            'haemophilia': {'trait': 'haemophilia','cTid1': False,'cTid2': True},
            'brownEyes': {'trait': 'brownEyes','cTid1': False,'cTid2': True},
            'maleInfertility': {'trait': 'maleInfertility','cTid1': False,'cTid2': False}
        }
    ),
    Person(
        "Paul","male",chromosomes = {
            'haemophilia': {'trait': 'haemophilia','cTid1': True,'cTid2': True},
            'brownEyes': {'trait': 'brownEyes','cTid1': False,'cTid2': True},
            'maleInfertility': {'trait': 'maleInfertility','cTid1': False,'cTid2': False}
        }
    )
#     Person(
#         "Denver","male",chromosomes = {
#             'curlyHair': {'trait': 'curlyHair','cTid1': True, 'cTid2': True}
#         }
#     )
]

traits = {
    'haemophilia': Phenotype(name='haemophilia',sexLinked='x',dominant=False,allele='h'),
    'brownEyes': Phenotype(name='brownEyes',sexLinked=False,dominant=True,allele='b'),
    'maleInfertility': Phenotype(name='maleInfertility',sexLinked='y',dominant=True,allele='i'),
#    'curlyHair': Phenotype(name='curlyHair',sexLinked=False,dominant=False,allele='c')
}

#dbi(db,1,str(people[3].testFor(traits['curlyHair'])))

"""
tempName = raw_input("Person's name: ")
tempGender = raw_input("Are they male or female?: ")
tempChromatid1 = raw_input("First chromatid?: ")
tempChromatid2 = raw_input("Second chromatid?: ")
tempPerson = Person(tempName,tempGender,tempChromatid1,tempChromatid2)
people.append(tempPerson)
"""

def listPeople():
    for person in people:
        dbi(db,3,"person","root_object",str(type(person)))
        dbi(db,1,"person",person.name,person.gender)
        for chromosome in person.chromosomes:
            #dbi(db,1,str(chromosome['trait']),str(chromosome['cTid1']),str(chromosome['cTid2']))
            dbi(db,2,"person",person.name,str(chromosome),str(person.chromosomes[chromosome]))
            
def listTraits():
    for trait in traits:
        dbi(db,3,"trait","root_object",str(type(traits[trait])))
        dbi(db,1,"trait",str(traits[trait].name),"sexLinked?",str(traits[trait].sexLinked))
        dbi(db,1,"trait",str(traits[trait].name),"dominant?",str(traits[trait].dominant))
        
def listPersonTestResults():
    for person in range(len(people)):
        for trait in traits:
            dbi(db,1,"DOES",people[person].name,"HAVE",traits[trait].name,str(people[person].testFor(traits[trait])))
            #dbi(db,1,people[person].calcGenotype(pass))
            
#listPeople()
#listTraits()
#listPersonTestResults()
