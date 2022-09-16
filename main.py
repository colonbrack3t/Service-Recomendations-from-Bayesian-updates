PARENTING = 0
SOCIAl = 1
FINANCIAL = 2
COUNSELING = 3

NUM_CATEGORIES = 4

class Question:
    #question string
    q_string = ""
    #weights for yes answer
    weights_yes = []
    #weights for no answer
    weights_no = []
    def __init__(self,q_string, weights_y,weights_n = 0):
        if weights_n == 0:
            #creates a inverse of the weights list
            weights_n = [1-x for x in weights_y]
        self.q_string = q_string
        self.weights_yes= weights_y
        self.weights_no = weights_n

class Service:
    service_name = ""
    weights = []
    def __init__(self, service_name, weights):
        self.service_name = service_name
        self.weights = weights
class BayesianUpdater:
    questions = []
    services = []
    states = [0.5]*NUM_CATEGORIES
    question_index = 0

    def __init__(self):
        self.questions.append(Question('Do you have kids?', [0.8,0.5,0.6,0.5]))
        self.questions.append(Question("Do you spend time with friends?", [0.5,0.1,0.4,0.4]))
        self.questions.append(Question("Do you have dark thoughts?", [0.5,0.6,0.5,0.9]))

        self.services.append(Service('Parent Group', [0.8,0.8,0,0]))
        self.services.append(Service('Samaritans', [0,0,0,0.8]))
        self.services.append(Service('Financial Advise', [0,0,0.8,0]))


    def AskQuestion(self):
        q = self.SelectQuestion()
        if 'y' in input(q.q_string):
            return q.weights_yes  
        return q.weights_no

    def SelectQuestion(self):
        index = 0#self.question_index%len(self.questions)
        self.question_index += 1
        return self.questions[index]

    def Update(self):
        data = self.AskQuestion()
        #print(data)
        for x in range(NUM_CATEGORIES):
            prior = self.states[x]
            d = data[x]
            #needs refining
            likelihood = ((d - prior) /2) + 0.5
            
            
            
            normalisation = 0.5
            #print(prior,d,likelihood)
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
        threshold =0.3 
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

    
bu = BayesianUpdater()
for _ in range(1000):
    bu.Cycle()
    input()
            
