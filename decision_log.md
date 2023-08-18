
## Technologies Evaluated
# LangChain

## Description
LangChain is a compelling multipurpose product for interacting with LLMs from various sources. It includes functionality for creating autonomous agents. It is a Python library

## Pros
- Familiar with the team
- Extensive documentation and examples
- Extensive tooling for various use cases

## Cons
- AutoGPT and BabyAGI integration is experimental
- AutoGPT functionality from experimental library seems to lack the tooling that comes with the main repo. You must provide it yourself

## Conclusion
It's highly likely we'll use LangChain in some capacity

# AutoGPT

## Description
AutoGPT takes in a starting prompt and uses a provided set of tools to accomplish the goals in the prompt. It can run from the command line or be incorporated into a larger project.

## Pros
- Inherently capable of research via search functionality

## Cons
- Experimental and can get stuck in a loop without no functionality to abort
- The AI drives the workflow so if it needs guidance on a technique of arriving to the best answer it may not follow it.

## Conclusion
We may be able to use AutoGPT for these purposes.

# BabyGPT

## Description
Similar to AutoGPT, it uses a vector database automatically to act as a memory.

## Pros
- Simple

## Cons
- Doesn't seem to support custom tooling and for that matter doesn't seem to support any tooling without modifying it ourselves. The vanilla version seems to do everything from the LLM's training.

## Conclusion
We will need internet search and other custom tooling so this is not a good fit.

# SuperAGI

## Description
Similar to AutoGPT but a much larger framework and built to be ran from a web page. SuperAGI feels more user friendly for non-technical users and has a lot of functionality in place to make it a compelling product once the rough edges are ironed out.

## Pros
- A lot out of the box, including logic, various configuration options, and a GUI
- Sponsoring Hackathon

## Cons
- missing documentation for use cases like creating sharable agent templates
- more complex to run locally
- Lack of guidance on how we would deploy a public facing demoable proof of concept
- Documentation gaps
- Agent workflows seem to be built at start-up for SuperAGI with no obvious guidance on how to add them later.
  - Could likely seed them via a script

## Conclusion
Since SuperGPT is sponsoring this hackathon, we feel obligated to use this. We feel confident in being able to build a solution, but it may be more work than using LangChain + Streamlit.

# Streamlit

## Description
A library for creating web interfaces using Python code, tailored towards data science and machine learning.

## Pros
- Free hosting
- Easy to use
- Plenty of examples and integrations with LangChain

## Cons
- Only free hosting, so limited to quotas
- Memory leaks are a risk if caching isn't leveraged properly

## Conclusion
This is a solid choice, but it doesn't seem capatible with SuperAGI since they both provide front-ends.

# Spikes
- Streamlit + AutoGPT via LangChain experimental - streamlit-app branch
- SuperAGI + custom toolkit - super-agi-toolkit branch

## Decisions
- 8/17/2023 - Heavily leaning towards SuperAGI + custom toolkit. We are still awaiting guidance on how best to demo. We have spent efforts in streamlining onboading via the dev container and GitHub Codespaces. We believe that using SuperAGI would be more effort than Streamlit + AutoGPT or LangChain, however based on the sponsorship of the Hackathon and the capabilities of SuperAGI, both current and future, we feel it is worth grinding through the challenge as it will provide the most value. This is not just an opportunity to build a research agent, its also an opportunity to become familiar with the capabilities of SuperAGI which may pay dividends in the future.
