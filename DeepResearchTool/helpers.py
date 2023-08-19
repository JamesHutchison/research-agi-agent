import logging

from superagi.llms.base_llm import BaseLlm


def do_chat_and_log_it(llm: BaseLlm, messages: list[dict]) -> str:
    logging.warning(messages)
    logging.warning("DOING CHAT")
    response = llm.chat_completion(messages)
    logging.warning(response)
    return response["content"]
