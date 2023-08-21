import os
import time

import openai
import pandas as pd
import tiktoken
from tqdm import tqdm

"""
examine.py
used after loader.py loaded datasets in to xlsx form, store with gpt generated result in new {dataset name}result.xlsx
"""


def trim_to_token_limit(text, max_tokens=3700):
    # specify token counting rule and max tokens count here, default 3.5 turbo with 3700 tokens
    # does not need to process truncated part, no specific impact in summarizing performance
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    if len(tokens) < max_tokens:
        return enc.decode(tokens)
    else:
        tokens = tokens[0:max_tokens]
        return enc.decode(tokens)


def gen_prompt(content, category):
    content = trim_to_token_limit(content)
    if category == 'academic':
        prompt = "You are writing an abstract for an academic research paper, return your generated abstract only. Do not left out important information. The main content of the paper is as given: " + content
    elif category == 'news':
        prompt = "You are given a cnn news piece, you need to write an abstractive summary bullets for it. The news story is as follows: " + content
    else:
        prompt = "Please summarize the given text. The text is as follows:" + content
    return prompt


def private_generate_summary(main_content, category):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant who writes summary based on different types of contents"},
                {"role": "user", "content": gen_prompt(main_content, category)},
            ],
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None


def public_generate_summary(main_content, category):
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant who writes summary based on different types of contents"},
                {"role": "user", "content": gen_prompt(main_content, category)},
            ],
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None


def get_type(path):
    file_name = path.split('/')[-1].strip('test.xlsx')
    if file_name == 'pubmed':
        return 'academic'
    elif file_name == 'cnn':
        return 'news'


def private_examine(path):
    # used for small scale personal testing
    openai.api_key = 'Your API Key'
    data = pd.read_excel(path, engine='openpyxl')
    data['Summary'] = ""
    request_interval = 20
    category = get_type(path)
    for index in tqdm(range(len(data))):
        start_time = time.time()
        paper_body = data.loc[index, 'Article']
        # calling private openai gpt for summary
        summary = private_generate_summary(paper_body, category)
        data.loc[index, 'Summary'] = summary
        elapsed_time = time.time() - start_time
        remaining_time = request_interval - elapsed_time
        if remaining_time > 0:
            time.sleep(remaining_time)
    data.to_excel('data/' + path.split('/')[-1].strip('test.xlsx') + 'result.xlsx', index=False, engine='openpyxl')


def public_examine(path):
    openai.api_type = "azure"
    openai.api_base = "https://bsaiuks.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    data = pd.read_excel(path, engine='openpyxl')
    data['Summary'] = ""
    request_interval = 4
    category = get_type(path)
    for index in tqdm(range(len(data))):
        start_time = time.time()
        paper_body = data.loc[index, 'Article']
        # calling public openai gpt for summary
        summary = public_generate_summary(paper_body, category)
        data.loc[index, 'Summary'] = summary
        elapsed_time = time.time() - start_time
        remaining_time = request_interval - elapsed_time
        if remaining_time > 0:
            time.sleep(remaining_time)
    data.to_excel('data/' + path.split('/')[-1].strip('test.xlsx') + 'result.xlsx', index=False, engine='openpyxl')


# examine loaded data with private or public openai engine
public_examine('data/pubmedtest.xlsx')
# private_examine('data/cnntest.xlsx')
