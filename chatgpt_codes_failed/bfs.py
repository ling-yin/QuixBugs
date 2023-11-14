import os
from dotenv import load_dotenv
import os
import openai
import time

load_dotenv()

correction = """Certainly! In the original code, there is a bug in the line `queue.extend(node for node in node.successors if node not in nodesseen)`. he issue is that the variable `node` is being used as both the loop variable and the variable representing the current node. This causes a conflict and leads to incorrect behavior. 

To fix this bug, we need to use a different variable name for the loop variable. In the corrected code, I have changed the loop variable to `successor`. 

Here is the corrected line: `queue.extend(successor for successor in node.successors if successor not in nodesseen)`. 

This line correctly extends the queue with the successors of the current node, excluding any successors that have already been seen. 

Additionally, I have made a similar correction in the line `nodesseen.update(node.successors)`. The corrected line is `nodesseen.update(successor for successor in node.successors if successor not in nodesseen)`. This ensures that only unseen successors are added to the `nodesseen` set. 

These corrections ensure that the breadth-first search algorithm works correctly and avoids any infinite loops or incorrect results."""

def extract_code(input_file_path):

    with open(input_file_path, 'r') as input_file:
        in_code_block = False
        extracted_code = []

        for line in input_file:
            if line.strip().startswith('"""'):
                break

            if not in_code_block:
                extracted_code.append(line)

    extracted_code_str = ''.join(extracted_code)
    # print(extracted_code_str)

    return extracted_code_str

def get_buggy_code_names(directory):
    new_directory = []
    for i in range(len(directory)):
        if "test.py" not in directory[i]:
            new_directory.append(directory[i])
            
    return new_directory

def call_api(buggy_code_inti, buggy_code_corrected): 
    retries = 0
    while retries < 3: 
        try: 
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant. You help to identify bugs in code."},
                    {"role": "user",
                    "content": f"Can you identify the bug in the following code: \n  ```\n {buggy_code_init}\n ```"},
                    {"role": "assistant", "content": f"```\n {buggy_code_corrected}\n ``` "},
                    {"role": "user", "content": "Can you explain the code correction?"},
                    {"role": "assistant", "content": f"{correction}"},
                    {"role": "user", "content": f"Can you explain the Breadth First Search Algorithm. And using that, correct the initial buggy code \n ```\n {buggy_code_init}\n ```"}

                ],
                temperature=0,
            )
            print(response)
            corrected_code = response["choices"][0]["message"]["content"]
            # print(corrected_code)
            return corrected_code
        except Exception as e:
            if e:
                print(e)
                print('Timeout error, retrying...')
                retries += 1
                time.sleep(5)
            else:
                raise e
    return False


def write_to_file(file_path, corrected_code):
    # Open the file in write mode and write the output text to it
    with open(file_path, "w") as file:
        file.write(corrected_code)



if __name__ == "__main__":
    # Set up Parameters 
    MODEL = os.environ.get('MODEL')
    openai.api_key = os.getenv("OPENAI_API_KEY")

    list_of_failed = ["breadth_first_search"]
    read_directory_og = "../python_programs/"
    read_directory_corrected = "../chatgpt_codes/"
    write_directory = "../chatgpt_codes_failed/"

    # Get the files containing the buggy code 
    # list_dir = os.listdir(read_directory_og)
    # list_dir = get_buggy_code_names(list_dir)

    # Iterate through the files, make API call and write to file
    for i in range(0, len(list_of_failed)): 
        write_file_path = write_directory + list_of_failed[i] + "fix2" + ".txt"
        read_file_path_buggy = read_directory_og + list_of_failed[i] + ".py"
        read_file_path_corrected = read_directory_corrected + list_of_failed[i] + ".py"

        buggy_code_init = extract_code(read_file_path_buggy)
        buggy_code_corrected = extract_code(read_file_path_corrected)
        corrected_code = call_api(buggy_code_init, buggy_code_corrected)

        if corrected_code != False: 
            write_to_file(write_file_path, corrected_code)
        # time.sleep(3)
            print(f"Status: {list_of_failed[i]} completed")
        else:
            # Log errors to retrieve 
            file_path = write_directory + "errors.txt"
            with open(file_path, "w") as file:
                file.write(f"Status: {list_of_failed[i]} failed")
            print(f"Status: {list_of_failed[i]} failed")





    # write_to_file("bfs.py", "test", write_directory)
    # print(len(list_dir))
