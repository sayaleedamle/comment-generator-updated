import json
import os
import requests
import sseclient
from comment_generator.configuration.config import cfg


def create_prompt(code):
    return f""" 
# Task Description: 
Your task is to generate comments for functions 

# Example
Here is an example on how you should do it - 
here is the input:
```python
def save_text_to_file(text):
    logger.info("in 2nd func")
    try:
        
        with open(cfg.transcribed_text / f"{{uuid.uuid4()}}.txt", "w") as file:
            file.write(text)
            logger.info("successful")
            return "success"
    except Exception as e:
        logger.exception("error")
        return str(e)```

This should be the output:
```python
def save_text_to_file(text):
    \"\"\"
    Saves the provided text to a file with a unique name.

    This function attempts to write the given text to a new file within the directory
    specified by `cfg.transcribed_text`. The file will have a unique name generated by
    `uuid.uuid4()`. If the operation is successful, it logs the success and returns the
    string "success". If an exception occurs, it logs the exception and returns the
    exception message as a string.

    :param text: The text to be saved to the file.
    :type text: str
    :return: "success" if the file is written successfully, otherwise the exception message.
    :rtype: str
    \"\"\"
    logger.info("in 2nd func")  # Log entry indicating the function has been entered.
    try:
        # Attempt to open a new file for writing in the directory specified by cfg.transcribed_text.
        # The filename is generated using uuid.uuid4() to ensure uniqueness.
        with open(cfg.transcribed_text / f"{{uuid.uuid4()}}.txt", "w") as file:
            file.write(text)  # Write the provided text to the file.
            logger.info("successful")  # Log entry indicating the write operation was successful.
            return "success"  # Return the string "success" to indicate success.
    except Exception as e:
        logger.exception("error")  # Log the exception with a message "error".
        return str(e)  # Return the exception message as a string.
```

# Instruction
Can you please add comments to all python functions using the reStructuredText Docstring Format for the following code
```python
{code}
```
"""


def comment_code_opensource(code):
    url = "https://api.together.xyz/inference"
    model = "togethercomputer/llama-2-70b-chat"

    payload = {
        "model": model,
        "max_tokens": 512,
        "prompt": create_prompt(code),
        "request_type": "language-model-inference",
        "temperature": 0,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stream_tokens": True,
        "stop": ["[/INST]", "</s>"],
        "negative_prompt": "",
        "sessionKey": "2e59071178ae2b05e68015136fb8045df30c3680",
        "type": "chat",
        "prompt_format_string": "[INST]  {prompt}\n [/INST]",
        "safety_model": "",
        "repetitive_penalty": 1,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {cfg.together_api_key}",
    }

    response = requests.post(url, json=payload, headers=headers, stream=True)
    response.raise_for_status()

    client = sseclient.SSEClient(response)
    output = ""
    for event in client.events():
        if event.data == "[DONE]":
            break

        partial_result = json.loads(event.data)
        token = partial_result["choices"][0]["text"]
        output += token
    return output


if __name__ == "__main__":
    code = """

def event_enhancement(events_list: List[str], urls: str) -> str:
    urls_list = json.loads(urls)
    url_map = {event["id"]: event for event in urls_list}
    for event in events_list:
        url_info = url_map.get(event["id"])
        if url_info is not None:
            event["url"] = url_info["url"]
    return json.dumps(events_list)


def extract_event_ids(events_list: List[dict]) -> List[int]:
    return [event["id"] for event in events_list]

"""

    print(comment_code_opensource(code))
