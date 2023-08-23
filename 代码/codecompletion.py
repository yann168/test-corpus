import json
import os

import openai
import pandas as pd
from evalplus.data import get_human_eval_plus, write_jsonl
from tqdm import tqdm


def generate_one_completion(prompt):
    try:
        prompt = "Complete the following Python code: Notes: respond with the entire complete function definitiondo not add any comments, be as concise in your code as possibleuse only built-in libraries, assume no additional imports other than those provided (if any)\ncode:" + prompt
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        if response.choices[0].finish_reason != "stop":
            print(f"Warning: completion did not finish: {response.choices[0].finish_reason}")
            return None
        else:
            return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating: {e}")
        return None


def generate_completions(num_samples_per_task):
    openai.api_type = "azure"
    openai.api_base = "https://bsaiuks.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Retrieve the problems dataset
    problems = get_human_eval_plus()
    # Choose the number of samples per task
    samples = [
        dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
        for task_id in tqdm(problems, desc="Generating samples")
        for _ in range(num_samples_per_task)
    ]
    write_jsonl(str(num_samples_per_task) + "samples.jsonl", samples)


def extract_function_body(code: str) -> str:
    lines = code.splitlines()
    function_lines = []
    inside_function = False
    for line in lines:
        # Detect the start of a function
        if line.strip().startswith("def "):
            inside_function = True
            continue  # Skip the function definition line
        # If we're inside a function, capture its lines
        if inside_function:
            if line.startswith((' ', '\t')) or line.strip() == '':
                function_lines.append(line)
            # Stop capturing when we hit a line that contains text but does not start with a whitespace character
            elif line.strip() != '' and not line.startswith((' ', '\t')):
                break
    return '\n'.join(function_lines)


def clean_code_and_save(path):
    solutions = []
    sanitized_solutions = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            solutions.append(json.loads(line))
            code_result = json.loads(line)['completion']
            sanitized_solutions.append(extract_function_body(code_result))

    df = pd.DataFrame(solutions)
    df['sanitized_solutions'] = sanitized_solutions
    df.to_excel(path.strip('.jsonl') + '.xlsx', engine='openpyxl')


def code_to_jsonl(path):
    excel_data = pd.read_excel(path.strip('.jsonl') + '.xlsx')
    values_to_modify = excel_data['sanitized_solutions'].tolist()
    with open(path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    for i, line in enumerate(lines):
        data = json.loads(line)
        data['completion'] = values_to_modify[i]
        modified_lines.append(json.dumps(data))
    with open("cleaned_" + path, 'w') as file:
        for line in modified_lines:
            file.write(line + '\n')


def main():
    k = 10
    generate_completions(k)
    path = str(k) + 'samples.jsonl'
    clean_code_and_save(path)
    code_to_jsonl(path)
    # After getting cleaned jsonl file, run the following command under the same directory using linux terminal
    # evalplus.evaluate --dataset humaneval --samples {YOUR_JSONL_FILE} --i-just-wanna-run

if __name__ == "__main__":
    main()
