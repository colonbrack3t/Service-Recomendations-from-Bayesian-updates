# Service Recomendations from Bayesian updates

Prototype for Service Recomendations using a Bayesian Update model

- Pros- user does not have to enter perfect paths

- Cons- scalability may be difficult

- TODO Use normal distribution for Services Categories

Useful tool for checking/creating Normal distributions: https://homepage.divms.uiowa.edu/~mbognar/applets/normal.html

## Explanation of approach

![image](https://user-images.githubusercontent.com/26506402/190587253-6b20b90b-365c-40ee-88cd-674a77b981b0.png)

This equation from Bayes Theorem posits that the updated posterior belief of a state A, given the evidence B, is proportional to the likelihood of evidence B given the prior belief in A, and the prior probability of A. 

In Layman's terms: The probability I am in state A given I have experienced some sensation B, is proportional to the probabilty of experiencing B given I am in state A, and what I thought the probabilty for A was before I experienced B

Thus, the Bayes Theorem is refered to as <b>posterior is proportional to the product of likelihood and prior</b>
# Implementation

## Common Weights Vertex / Categories
For this implementation, first I defined a common weight dictionary format which all the parts of the algorithm will use. These weights represent a distribution for the probability of the category represented by that weight.

The weight matrix example has 4 catergories, in this order:

`{Parenting : , Social : , Financial : , Counsel : }`

The nuance of these categories, when applied to various parts of the application, will be explained in those appropriate parts. The categories are declared as constants with corresponding indices to ensure continuity throughout the code.

The types of the values in this matrix will also vary, depending on where this is being applied.

## Services
I implemented a class Service to represent the service options the algorithm provides. A given Service has a name and a Weight Matrix. A full version of this product should store a foreign key to the Service in a seperate DB. 

For a given Service, the weights represent the probability someone who needs a given category would use this service. You can think of it as 'does this service provide this category'. For example, a Parent Group (where multiple parents go to some common location to look after their children together and socialise) would provide a Parenting and Social support, but not a Financial or Counsel support. Thus the weights for this Service are set to [1,1,0,0]

## Questions & Question Category Probability
The Question class represents a given question in the survey. It contains the question (expected to always be yes/no), a 'yes' weights and 'no' weights. If only presented with a 'yes' weights, it will generate the inverse for 'no' weights on its own. Answering a question will create a new 'evidence' or 'experience' which we will use in the Bayes equation to create our 'likelihood'.

The weights here represents the probability of someone needing a given category, and their type is Question Category Probability. This class represents a normal distribution, and contains a function for calculating the likelihood of a given state from this observation. In order to declare QCP objects, I have included constants for values of standard deviation which give good results on the given data. 

## Bayesian Updater
The Bayesian Updater has a number of attributes. The questions and services arrays are for storing and referencing. It also contains a weights vertex, which represents the Updater's belief in the user's needs. It is initialised as an array of 0.5s as this represents no favour (50-50 chance to be relevant)

The constructor is responsible for creating and adding questions and services to the collection. The cycle function is the main entry point for the updater. Each time it is called, it will prompt the console with a question. A response is considered a 'yes' if it includes a 'y' character. 

When a question is answered, for each category in the Bayesian weights vertex, we update our belief using the same category from the likelihood function provided by the answer, our prior belief in the category and a normalisation value (to ensure the posterior remains as a value between 1 and 0).

Finally, the BestSolutions function is called which checks the Pythagoreon distance of the weights and each service, and if the distance is below a threshold it is suggested to the user.

Repeatedly calling the cycle funciton will loop through the questions, each time updating and refining the belief in the weights.
