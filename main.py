'''
Library imports
'''
import sys
from math import pi, exp
from scipy.stats import norm

'''
Constants
'''

PARENTING = 0
SOCIAL = 1
FINANCIAL = 2
COUNSELING = 3
#copy & paste to create legible dicts or use category_dict.copy() to create an instance of this dict
category_dict = {
    PARENTING : 0.5,
    SOCIAL : 0.5,
    FINANCIAL : 0.5,
    COUNSELING : 0.5
}

NUM_CATEGORIES = 4

'''
Use these preset standard deviations for creating distributions
'''

CERTAIN_PROBABILTY_SD = 0.5
MEDIUM_PROBABILITY_SD = 1
UNCERTAIN_PROBABILITY_SD = 3



class QuestionCategoryProbability:
    """This class represents a Normal Distribution probability for a given question's category
    """
    mean = 0
    standard_deviation = 0
    def __init__(self, m:float, sd:float):
        """Constructor

        Args:
            m (float): mean
            sd (float): standard deviation
        """
        
        self.mean = m
        self.standard_deviation = sd
    def likelihood(self,x:float) ->float:
        """Likelihood estimation. Uses CDF
        Args:
            x (float): given state
        
        Returns:
            float: Likelihood of observed question, given state x
        """
        return norm(x,self.standard_deviation).cdf(self.mean)
    def inverse(self):
        """Inverts this QCP mean
        """
        self.mean = 1- self.mean
    def __str__(self):
        return f"mean = {self.mean}, sd = {self.standard_deviation}"

class Question:
    #question string
    m_question_string = ""
    #weights for yes answer
    weights_yes : dict = {}
    #weights for no answer
    weights_no : dict = {}
    def Set_Collection_as_weights(self, weights_y, weights_n):
        """Generalised function for turning array or dict of weights input to constructor into the weights array for this class

        Args:
            weights_y : Weights for 'yes' response
            weights_n : Weights for 'no' response
        """

        for i in range(NUM_CATEGORIES):
                vy = weights_y[i]
                vn = weights_n[i]

                #unknown desired probability, as only mean value presented, so assume a medium SD
                QCP_y = QuestionCategoryProbability(vy,UNCERTAIN_PROBABILITY_SD)
                QCP_n = QuestionCategoryProbability(vn,UNCERTAIN_PROBABILITY_SD)
                self.weights_yes[i] = QCP_y
                self.weights_no[i] = QCP_n 

    def __init__(self,q_string:str,**kwargs):
        """
        Args:
            q_string (str): Question text
            **flat_array_y : array of floats representing average for each category, for 'yes' response
            **flat_array_n : (Optional, will be generated from inverse of y if omitted)
            
            **flat_dict_y : dict of floats representing average for each category, for 'yes' response
            **flat_dict_y : (Optional, will be generated from inverse of y if omitted)
            
            **distributions_yes : dict of QuestionCategoryProbability for 'yes' response
            **distributions_yes : (Optional, will be generated from inverse of yes if omitted)

        """
        #create copys so that they do not point to the same dict obj in memory
        self.weights_yes = category_dict.copy()
        self.weights_no = category_dict.copy()
        self.m_question_string = q_string
        #option for 'simple' array of probability values
        if 'flat_array_y' in kwargs:
            weights_y = kwargs['flat_array_y']
            if not 'flat_array_n' in kwargs:
                #creates a inverse of the weights list
                weights_n = [1-x for x in weights_y]
            else:
                weights_n = kwargs['flat_array_n']
            self.Set_Collection_as_weights(weights_y,weights_n)
             
        elif 'flat_dict_y' in kwargs:
            weights_y = kwargs['flat_dict_y']
            if not 'flat_dict_n' in kwargs:
                #creates inverse of the dict, with same keys
                #eg {1 : 0.1, 2 : 0.5} -> {1 : 0.9, 2 : 0.5}
                weights_n = {k: 1-v for k,v in weights_y.items()}
            else:
                weights_n = kwargs['flat_dict_n']
            self.Set_Collection_as_weights(weights_y,weights_n)      
        elif 'distributions_yes' in kwargs:
            weights_y = kwargs['distributions_yes']
            if not 'distributions_no' in kwargs:
                #creates inverse of the dict, with same keys
                #eg {1 : 0.1, 2 : 0.5} -> {1 : 0.9, 2 : 0.5}
                weights_n = {k: v.inverse() for k,v in weights_y.items()}
            else:
                weights_n = kwargs['distributions_no']
            
            self.weights_yes = weights_y
            self.weights_no = weights_n
          
    def __str__(self):
        return f'{self.m_question_string}, weights_yes = [{[str(k) + " " +  str(v) for k,v in self.weights_yes.items()]}], weights_no = [{[str(k)  + " " +  str(v)  for k,v in self.weights_no]}]'
class Service:
    service_name = ""
    weights = []
    def __init__(self, service_name:str, weights:list):
        """
        Args:
            service_name (str): Name of service
            weights (list): float list of weights for each category for service
        """
        self.service_name = service_name
        self.weights = weights
        
class BayesianUpdater:
    questions = []
    services = []
    states = category_dict.copy()
    question_index = 0
    log = False
    def __init__(self,log = False):
        """
        Args:
            log (bool, optional): If true, additional print statements showing internal calculations. Defaults to False.
        """
        self.log = log
        self.questions.append(Question('Do you have kids?', flat_array_y = [0.8,0.5,0.6,0.5]))
        self.questions.append(Question("Do you spend time with friends?", flat_array_y = [0.5,0.1,0.4,0.4]))
        self.questions.append(Question("Do you have dark thoughts?", flat_array_y = [0.5,0.6,0.5,0.9]))

        self.questions.append(Question('Do you need Financial Advise?', 
        distributions_yes={
            PARENTING : QuestionCategoryProbability(0.5,UNCERTAIN_PROBABILITY_SD),
            SOCIAL : QuestionCategoryProbability(0.5,UNCERTAIN_PROBABILITY_SD),
            FINANCIAL : QuestionCategoryProbability(0.9,CERTAIN_PROBABILTY_SD),
            COUNSELING : QuestionCategoryProbability(0.5,UNCERTAIN_PROBABILITY_SD),
        },
        distributions_no={
            PARENTING : QuestionCategoryProbability(0.5,UNCERTAIN_PROBABILITY_SD),
            SOCIAL : QuestionCategoryProbability(0.5,UNCERTAIN_PROBABILITY_SD),
            FINANCIAL : QuestionCategoryProbability(0.2,MEDIUM_PROBABILITY_SD),
            COUNSELING : QuestionCategoryProbability(0.5,UNCERTAIN_PROBABILITY_SD),
        }))

        self.services.append(Service('Parent Group', [0.8,0.6,0.5,0.5]))
        self.services.append(Service('Samaritans', [0.5,0.6,0.5,0.8]))
        self.services.append(Service('Financial Advise', [0.6,0.5,1,0.5]))


    def AskQuestion(self):
        q : Question = self.SelectQuestion()
        if 'y' in input(q.m_question_string):
            return q.weights_yes  
        return q.weights_no

    def SelectQuestion(self) -> Question:
        index = self.question_index%len(self.questions)
        self.question_index += 1
        return self.questions[index]

    def CalculateNormalisation(self, data:list, d:QuestionCategoryProbability):
        return 0.5
        
    def Update(self):
        data = self.AskQuestion()

        for x in range(NUM_CATEGORIES):
            prior = self.states[x]
            d : QuestionCategoryProbability = data[x]
            likelihood = d.likelihood(prior)
            normalisation = self.CalculateNormalisation(data,d)
            if self.log:
                print(x, 'Prior:',prior,', z mean:',d.mean,',\nz standard deviation:',d.standard_deviation,', Likelihood:',likelihood)
            
            #Bayesian Update:
            posterior = (prior * likelihood)/normalisation
           
            self.states[x] = posterior
    def CalculateDistanceOfWeights(self,service_weights:dict)->float:
        squared_sum = 0
        for x in range(NUM_CATEGORIES):
            euclidean_dist = service_weights[x] - self.states[x]
            squared_dist = pow(euclidean_dist,2)
            squared_sum += squared_dist
        
        return pow(squared_sum, 0.5)
    
    def BestSuggestion(self):
        threshold =1
        suggestions = []
        for i in range(len(self.services)):
            service = self.services[i]
            dist = self.CalculateDistanceOfWeights(service.weights)
            if self.log:
                print('Service:', service.service_name, ', Distance:',dist)
            if dist < threshold:
                suggestions.append((service, dist))
        return suggestions
    
    def Cycle(self):
        """Asks question, updates weights, then offers suggestions
        """
        self.Update()
        for s,d in self.BestSuggestion():
            print(s.service_name, f'{round((1 - d) * 100) }%')
        if self.log:
            print('Current belief:',self.states)

if __name__ == "__main__":
    print("TODO : Change Services to use Normal Distribution using QuestionCategoryProbability")
    log = '-v' in sys.argv
    if not log:
        print("\nbtw, run this with -v for verbose mode :)\n")
    bu = BayesianUpdater(log=log)
    for _ in range(1000):
        bu.Cycle()
        input()
            
