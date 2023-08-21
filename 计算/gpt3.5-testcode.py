#Note: The openai-python library support for Azure OpenAI is in preview.
import random
import os
import openai
import numpy as np
import pandas as pd
import time
openai.api_type = "azure"
openai.api_base = "https://bsaiuks.openai.azure.com/"
openai.api_version = ""
openai.api_key = "api key"

#num = [random.randint(0, 20442) for i in range(100)]
#print(num)
choices = ["A", "B", "C", "D", "E", "F", "G"]
engine = ['gpt-4', 'gpt-35-turbo']
def format_subject(subject):
    l = subject.split("_")
    s = ""
    for entry in l:
        s += " " + entry
    return s


def format_example(df, idx, include_answer=True):
    prompt = df.iloc[idx, 0]
    k = df.shape[1] - 2
    for j in range(k):
        prompt += "\n{}. {}".format(choices[j], df.iloc[idx, j+1])
    prompt += "\nAnswer:"
    if include_answer:
        prompt += " {}\n\n".format(df.iloc[idx, k + 1])
    return prompt


def gen_prompt(train_df, subject, k=-1):
    if k == -1:
        k = train_df.shape[0]
    for i in range(k):
        prompt += format_example(train_df, i)
    return prompt


subjects = ['emergent_properties']

all_cors = []
for subject in subjects:
    cors = []
    answer = []
    shot = 5
    dev_df = pd.read_csv(os.path.join(
        'data', subject + ".csv"), header=None)[:shot]
    test_df = pd.read_csv(os.path.join(
        'data', subject + ".csv"), header=None)
    for i in range(test_df.shape[0]):
    #for i in num:
        while True:
            prompt1 = "The following are multiple choice questions.\n (with answers) about {}.\n\n".format(
                format_subject(subject))
            if subject == 'question_selection':
                prompt1 += 'please choose the best question to fit the answer above.'
            if subject == 'qa_wikidata':
                prompt1 = "Please answer the following questions."
            test = format_example(test_df, i, include_answer=False)
            try:
                prompt1 = "The following are multiple choice questions.\n (with answers) about {}.\n\n".format(format_subject(subject))
                if subject == 'question_selection' :
                    prompt1 += 'please choose the best question to fit the answer above.'
                if subject == 'qa_wikidata':
                    prompt1 = "Please fill in the following blank."
                    print(prompt1, test)
                test = format_example(test_df, i, include_answer=False)
                #print(prompt1, test)
                #train_prompt = gen_prompt(dev_df, subject, shot)
                c = openai.ChatCompletion.create(
                    engine='gpt-35-turbo',
                                    messages=[{"role": "system", "content": prompt1},
                                            {"role": "user", "content": test }],
                                    temperature=0.7, max_tokens=800, top_p=0.95, frequency_penalty=0, presence_penalty=0, stop=None
                                        )
                break
#################################
            except:
                print("pausing")
                time.sleep(1)
                continue
        #print(c["choices"][0]["message"].content)
        pred = c["choices"][0]["message"].content[0]
        print(pred,end='')
        label = test_df.iloc[i, test_df.shape[1]-1]
        answer.append(pred)
        cor = pred == label
        cors.append(cor)
    acc = np.mean(cors)
    print("Average accuracy {:.3f} - {}".format(acc, subject))
    all_cors.append(cors)
    test_df["gpt-35-turbo correct"] = cors
    test_df["gpt-35-turbo answer"] = answer
    test_df.to_csv(os.path.join("results","results_{}".format(
        'gpt-35-turbo'), "{}.csv".format(subject)), index=None)
weighted_acc = np.mean(np.concatenate(all_cors))
print("Average accuracy: {:.3f}".format(weighted_acc))
