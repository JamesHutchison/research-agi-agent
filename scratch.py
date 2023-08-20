from langchain import GoogleSearchAPIWrapper

search_query = '"Study on health risks associated with fluoride consumption"'

search = GoogleSearchAPIWrapper()
# simple logic - top 3 results for now
TOP_N_RESULTS = 3
search_results = search.results(search_query, TOP_N_RESULTS)
print(search_results)
links = [result["link"] for result in search_results]
print(links)
