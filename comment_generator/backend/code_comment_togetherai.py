import datetime
import pathlib
import uuid
import together

from comment_generator.config_toml import cfg


def add_comments(model_name, code):
    together.api_key = cfg.together_api_key
    streamed_output = ""
    for output in together.Complete.create_streaming(
        prompt=f""" 
# Task Description: 
Your task is to generate comments for Python functions 

# Example
Here is an example on how you should do it - 
here is the input:
```python
def save_text_to_file(text):
    logger.info("in 2nd func")
    try:
        
        with open(cfg.transcribed_text / f"{uuid.uuid4()}.txt", "w") as file:
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
        with open(cfg.transcribed_text / f"{uuid.uuid4()}.txt", "w") as file:
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
""",
        model=model_name,
        max_tokens=512,
        temperature=0.1,
        top_k=50,
        top_p=0.7,
        repetition_penalty=1,
        stop=["<human>", "\n\n"],
    ):
        streamed_output += output
    d = datetime.datetime.now()
    d = str(d).replace(":", "")
    d = d.replace(" ", "")
    date_now = d[:14]
    print(date_now)
    code_comment = cfg.code_comment
    index = model_name.find("/")  # stores the index of a substring or char
    model = model_name[index + 1 :]

    code_comment_path = pathlib.Path(f"{code_comment}/exec_{date_now}")
    if not code_comment_path.exists():
        code_comment_path.mkdir(exist_ok=True, parents=True)
    with open(code_comment_path / f"{model}.txt", mode="w") as f:
        f.write("============")
        f.write("\n")
        f.write(streamed_output)
        f.write("\n")
        f.write("============")
        f.write("\n")
    return streamed_output


if __name__ == "__main__":
    for model in cfg.model_llama:
        print(model)
        code = """

        def save_text_to_file(text):
            logger.info("in 2nd func")
            try:
                
                with open(cfg.transcribed_text / f"{uuid.uuid4()}.txt", "w") as file:
                    file.write(text)
                    logger.info("successful")
                    return "success"
            except Exception as e:
                logger.exception("error")
                return str(e)
        """
        print(add_comments(model, code))
