import os
from dotenv import load_dotenv
import os
import openai
import time

load_dotenv()

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
                    {"role": "user", "content": "Can you explain the code correction?"}
                ],
                temperature=0,
            )
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

    list_of_failed = ["breadth_first_search", "detect_cycle", "get_factors", "lis", "max_sublist_sum", "possible_change", "powerset", "shortest_path_length", "subsequences", "wrap"]
    read_directory_og = "./python_programs/"
    read_directory_corrected = "./chatgpt_codes/"
    write_directory = "./chatgpt_codes_failed/"

    # Get the files containing the buggy code 
    # list_dir = os.listdir(read_directory_og)
    # list_dir = get_buggy_code_names(list_dir)

    # Iterate through the files, make API call and write to file
    for i in range(0, len(list_of_failed)): 
        write_file_path = write_directory + list_of_failed[i] + ".txt"
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
