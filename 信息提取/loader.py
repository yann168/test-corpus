import ast
import os

import pandas as pd

"""
loader.py
loading downloaded dataset pubmed or cnn stories, truncating redundant part and stored as html in columns
"""


def truncate_text_at_keyword(filename, keyword, count, new_filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    keyword_count = 0
    truncated_lines = []
    for line in lines:
        keyword_count += line.count(keyword)
        if keyword_count < count:
            truncated_lines.append(line)
        else:
            # Find the exact position of the keyword's nth occurrence and truncate
            remaining = count - (keyword_count - line.count(keyword))
            pos = find_nth_occurrence(line, keyword, remaining)
            truncated_lines.append(line[:pos])
            break

    # Save the truncated text as a new file
    with open(new_filename, 'w', encoding='utf-8') as new_file:
        new_file.writelines(truncated_lines)


def find_nth_occurrence(string, substring, n):
    positions = [i for i in range(len(string)) if string.startswith(substring, i)]
    try:
        return positions[n - 1]
    except IndexError:
        return -1


def load_pubmed(num):
    # num specifies total articles to load in xlsx
    with open('data/pubmed.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    paper = text.split('"article_text": ', num)[1:]
    article = []
    abstract = []
    for content in paper:
        separated_content = content.split('"abstract_text": ')
        clean_article = ast.literal_eval(separated_content[0].strip(', '))
        article.append("".join(clean_article))
        clean_abstract = ast.literal_eval(separated_content[1].split('"]')[0] + '"]')
        abstract.append("".join(clean_abstract).replace('<S> ', '').replace(' </S>', ''))
    df = pd.DataFrame({'Article': article, 'Abstract': abstract})
    df.to_excel('data/pubmedtest.xlsx', index=False, engine='openpyxl')


def list_files(dir_path, n):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files[:n]:
            file_list.append(os.path.join(root, file))
    return file_list


def load_cnn(num):
    article = []
    highlight = []
    stories = read_stories('data/cnn.txt')
    for story in stories[:num]:
        text = story.replace('\n', '').replace(r"\'", "'")
        separated_content = text.split('@highlight')
        article.append(separated_content[0])
        highlight.append(". ".join(separated_content[1:]) + '.')
    df = pd.DataFrame({'Article': article, 'Highlight': highlight})
    df.to_excel('data/cnntest.xlsx', index=False, engine='openpyxl')


def join_stories(num):
    dir_path = "data/cnn/stories"
    file_list = list_files(dir_path, num)
    text = []
    for path in file_list:
        with open(path, 'r', encoding='utf-8') as file:
            text.append(file.read())
            text.append('\n***END_OF_STORY***\n')
    text = "".join(text)
    with open('data/cnn.txt', 'w', encoding='utf-8') as file:
        file.write(text)


def read_stories(path):
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    stories = text.split('\n***END_OF_STORY***\n')  # 使用特殊分隔符来分割字符串
    # Remove the last element if it is empty
    if stories[-1] == '':
        stories.pop()
    return stories


# truncated 250mb txt file to 100 articles only for uploading on github
# truncate_text_at_keyword('data/test.txt', 'article_text', 101, 'data/pubmed.txt')
# join 30 cnn stories from 90000+ files, for uploading as well
# join_stories(30)

# load target dataset
load_pubmed(100)
# load_cnn(30)
