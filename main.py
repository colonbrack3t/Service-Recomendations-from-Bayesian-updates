
from math import pi, exp
from scipy.stats import norm

PARENTING = 0
SOCIAl = 1
FINANCIAL = 2
COUNSELING = 3
#copy & paste to create legible dicts
category_dict = {
    PARENTING : 0.5,
    SOCIAl : 0.5,
    FINANCIAL : 0.5,
    COUNSELING : 0.5
}
NUM_CATEGORIES = 4

CERTAIN_PROBABILTY_SD = 0.05
MEDIUM_PROBABILITY_SD = 0.1
UNCERTAIN_PROBABILITY_SD = 0.5

class QuestionCategoryProbability:
    mean = 0
    standard_deviation = 0
    def __init__(self, m, sd):
        self.mean = m
        self.standard_deviation = sd
    def likelihood(self,x):
        
        return norm.(self.mean,self.standard_deviation).cdf()
    def inverse(self):
        self.mean = 1- self.mean
    def __str__(self):
        return f"mean = {self.mean}, sd = {self.standard_deviation}"
all_qs = []
class Question:
    #question string
    m_question_string = ""
    #weights for yes answer
    weights_yes = 0
    #weights for no answer
    weights_no = 0
    def Set_Collection_as_weights(self, weights_y, weights_n):
        for i in range(NUM_CATEGORIES):
                #unknown desired probability, as only mean value presented, so assume a medium SD
                vy = weights_y[i]
                vn = weights_n[i]
                QCP_y = QuestionCategoryProbability(vy,UNCERTAIN_PROBABILITY_SD)
                QCP_n = QuestionCategoryProbability(vn,UNCERTAIN_PROBABILITY_SD)
                self.weights_yes[i] = QCP_y
                self.weights_no[i] = QCP_n 
    def __init__(self,q_string,**kwargs):
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
    def __init__(self, service_name, weights):
        self.service_name = service_name
        self.weights = weights
        
class BayesianUpdater:
    questions = []
    services = []
    states = category_dict.copy()
    question_index = 0

    def __init__(self):
        self.questions.append(Question('Do you have kids?', flat_array_y = [0.8,0.5,0.6,0.5]))
        self.questions.append(Question("Do you spend time with friends?", flat_array_y = [0.5,0.1,0.4,0.4]))
        self.questions.append(Question("Do you have dark thoughts?", flat_array_y = [0.5,0.6,0.5,0.9]))

        self.services.append(Service('Parent Group', [1,1,0,0]))
        self.services.append(Service('Samaritans', [0,0.5,0,1]))
        self.services.append(Service('Financial Advise', [0,0,1,0]))


    def AskQuestion(self):
        q = self.SelectQuestion()
        if 'y' in input(q.m_question_string):
            return q.weights_yes  
        return q.weights_no

    def SelectQuestion(self):
        index = self.question_index%len(self.questions)
        self.question_index += 1
        return self.questions[index]
    def CalculateLikelihood(self, d, prior):
        centralise_data = d - 0.5
        #naive likelihood calculation
        likelihood = prior + centralise_data
        likelihood = max(likelihood, 0.000001)
        likelihood = min(likelihood, 0.999999)

        return d#likelihood
    def CalculateNormalisation(self, data, d):
        return 0.5
        
    def Update(self):
        data = self.AskQuestion()
        #print(data)
        for x in range(NUM_CATEGORIES):
            prior = self.states[x]
            d = data[x]
            #needs refining
            likelihood = d.likelihood(prior)
            
            
            
            normalisation = 4# self.CalculateNormalisation(data,d)
            print(prior,d.mean,d.standard_deviation,likelihood)
            posterior = (prior * likelihood)/normalisation
           
            self.states[x] = posterior
    def CalculateDistanceOfWeights(self,service_weights):
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
            print(dist)
            if dist < threshold:
                suggestions.append(service)
        return suggestions
    
    def Cycle(self):
        self.Update()
        for s in self.BestSuggestion():
            print(s.service_name)
        print(self.states)

if __name__ == "__main__":
 
    bu = BayesianUpdater()
    for _ in range(1000):
        bu.Cycle()
        input()
            
