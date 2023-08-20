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

# Quickstart
This repo has a dev container configuration. Simply create a new Codespace in GitHub.

# SuperAGI tooling breakdown
If we use SuperAGI for implementing this agent, here are the components and capabilities we see necessary

## Capabilities
- Internet Search - The agent needs to be able to input aquery and derive one or more web URLs it believes is worth visiting
- Internet Scraping - The agent needs to be able to load a web page and read the contents. It needs to support web pages that require javascript
- Internal memory requirements:
  - The agent needs to be able to read a scraped web page and take relevant notes like a human would. The agent needs to be able to store these notes somewhere for later review
  - Having a vector database does not seem to be a requirement as the agent is to be thorough and will employ a dividge and conquer strategy for doing research. Notes are not expected to be so dense it can't fit in the context.
  - The agent likely needs a way to get a high level view of what it has done, what it has left to do, and what it should do next
- Output requirements:
  - The agent needs to be able to generate a potentially large markdown file or set of files and provide them to the user
  - The agent may be able to generate images and would need to be able to reference them in the markdown files
  - The agent may be able to generate code and would need to be able to display them
- Coherency requirements:
  - The agent cannot get stuck in a loop
  - The agent should progressively solve tasks and avoid falling down rabbit holes
  - The agent should clearly recognize when it is done researching
  - The agent should not get side-tracked and start solving irrelevant tasks

## Components
- Internet search - this is provided by SuperAGI
- Scholarly article search - out of scope for this hackathon
- Internet scraping - This is provided by SuperAGI
- Deep Research Toolkit - We will create this
  - Deep Research Tool - Will initialize the process and help the AI coordinate its thoughts and notes
  - Research Article Generation Tool - Will generate the markdown document containing the findings and results
  - Other bridge tools - We will need to evaluate how, for example, we would get the AI to read a scraped article in the context of this research.

# How to run
- Start a codespace
- Populate the .env file with:
  - `GOOGLE_API_KEY`
  - `GOOGLE_CSE_ID`
- Once it finishes the postStartCommand:
  - Run the "Run backend and Celery" run configuration
  - Run the task (Terminal menu -> Run Task) "Start Super AGI Docker containers"
  - Go to the "Ports" tab and change 3000 to a public port, then click on the planet icon when you hover your mouse over the "Local Address" cell for it

# Shortcut to Summary Debugging
- To avoid rerunning the agent when developing the summary generation, there is a script summary_debug.py in the root directory
- Populate the .env file with:
  - `OPENAI_API_KEY`
- The run configuration "Run summary debug" will run this
