# -*- coding:gbk -*-
import os
import re
import time
import logging
from tqdm import tqdm
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.llms import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ['OPENAI_API_KEY']='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'
#os.environ['OPENAI_API_KEY']='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'

template="""
�����ǿ�����������ص���ʵ: {fact}
����: {ques}
��:
"""


output='result/triple-chatgpt.txt'
data='../rewrite/output/chinese-alpaca-2-7b.txt'    

correct=0
all=0
cost=0
max_retries=100
# llm = OpenAI(model='text-ada-001',temperature=0)
llm = ChatOpenAI(model='gpt-3.5-turbo',temperature=0)
f1=open(output,'a',encoding='utf-8')
with open(data,'r',encoding='utf-8') as f:
    for index,line in tqdm(enumerate(f.readlines())):
        line=line.strip().split('\t')
        ques=line[0]
        if len(line)==2:
            fact=''
        else:
            fact=line[-1]
        ans=line[1].split('|')
        prompt=template.format(ques=ques,fact=fact)
        # set retry to prevent connect error
        retries = 0
        while retries < max_retries:
            try:
                with get_openai_callback() as cb:
                    response=llm.predict(prompt)
                    result='incorrect'
                    for i in ans:
                        if i.lower() in response.lower():
                            result='correct'
                            correct+=1
                            break
                f1.write('{}\t{}\t{}\t{}\t{}\n'.format(ques,fact.replace('\n',' ').replace('\t',' '),response.replace('\n',' ').replace('\t',' '),'|'.join(ans),result))
                cost+=cb.total_cost
                logging.info('Total Cost from Begin (USD): ${}'.format(cost))
                logging.info('Finish {}'.format(index+1))
                logging.info('Correct {}'.format(correct))
                logging.info('Current Accuracy {}'.format(correct/(index+1)))
                break  # Break the while loop if the request is successful
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                logging.info("Retrying in 10 minutes...")
                time.sleep(600)  # Wait for 10 minutes before retrying
                retries += 1  # Increment the number of retries
        all+=1
f1.close()
logging.info('Accuracy {}'.format(correct/all))
