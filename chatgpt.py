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

def call_api(buggy_code): 
    retries = 0
    while retries < 3: 
        try: 
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant. You help to identify bugs in code. You will provide answers containing only the corrected code, without explanations"},
                    {"role": "user",
                    "content": f"Can you identify the bug in the following code: \n  ```\n {buggy_code}\n ```"},
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
    read_directory = "./python_programs/"
    write_directory = "./chatgpt_codes/"

    # Get the files containing the buggy code 
    list_dir = os.listdir(read_directory)
    list_dir = get_buggy_code_names(list_dir)

    # Iterate through the files, make API call and write to file
    for code_file in list_dir: 
        write_file_path = write_directory + code_file
        read_file_path = read_directory + code_file

        buggy_code = extract_code(read_file_path)
        corrected_code = call_api(buggy_code)

        if corrected_code != False: 
            write_to_file(write_file_path, corrected_code)
        # time.sleep(3)
            print(f"Status: {code_file} completed")
        else:
            # Log errors to retrieve 
            file_path = write_directory + "errors.txt"
            with open(file_path, "w") as file:
                file.write(f"Status: {code_file} failed")
            print(f"Status: {code_file} failed")





    # write_to_file("bfs.py", "test", write_directory)
    # print(len(list_dir))
