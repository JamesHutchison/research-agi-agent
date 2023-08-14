# research-agi-agent
Hackathon project - An AGI agent for doing research, understanding, and validation

# Input
The user will provide a claim and known supporting information that they wish to research.

# Output
The AGI agent will generate a research document summarizing the claim, the ramifications, related facts. The agent will generate a conclusion that may include areas of further research that are necessary to help substantiate the claim, or the conclusion may point to concrete evidence that refutes the claim.

# Algorithm (draft - WIP)
- User enters claim
- User describes expert that would investigate the claim
- User adds information they feel is relevant
- AI will have multiple roles:
  - Initiator - AI acting on behalf of the user that elaborates on the user's claim and information with its own information that may support the claim. The initiator does not attempt to refute its own claim. The initiator is in charge of deciding whether they are satisified with the research or if there are unknowns worth further investigating.
  - Expert - Tries to find holes in the claim and scrutinizes it. It also attempts to provide facts that could support the claim and refute it.
  - Researcher - Takes information from the initiator and expert and checks facts and researches topics and concepts to help richen the knowledge in the context which the actors are working
  - Mathematician and Programmer - If needed, determines whether there are relevant mathematical models which could be applied that would help refute or support the claim, and then creates code to run the model against known facts.
  - Summarizer - After the initiator is satisified, aggregates the exchange between the roles and produces a document. Bonus points if it can generate visualizations.
