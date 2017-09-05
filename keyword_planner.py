
# coding: utf-8
from googleads import adwords
import json
import pandas as pd
import time
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('UTF8')


def get_language_code(language):
    with open('./languagecodes.json', 'r') as readfile:
        json_data = json.load(readfile)
        return json_data[language]


def get_country_code(country_code):
    cn = pd.read_csv('./countries.csv')
    cn.set_index('Country Code', inplace=True)
    return cn['Criteria ID'][country_code.upper()]


def get_volume(keywords, country, language):
    keywords = filter(None, keywords)
    language_code = get_language_code(language)
    adwords_client = adwords.AdWordsClient.LoadFromStorage('~/auth.yaml')
    targeting_idea_service = adwords_client.GetService(
        'TargetingIdeaService', version='v201609')

    selector = {
        'searchParameters': [
            {
                'xsi_type': 'RelatedToQuerySearchParameter',
                'queries': keywords,
            },
            {
                'xsi_type': 'LanguageSearchParameter',
                'languages': [{'id': str(language_code)}]
            },
            {
                'xsi_type': 'LocationSearchParameter',
                'locations': [{'id': country}]
            }
        ],
        'ideaType': 'KEYWORD',
        'requestType': 'STATS',
        'requestedAttributeTypes': ['KEYWORD_TEXT', 'SEARCH_VOLUME'],
        'paging': {
            'startIndex': '0',
            'numberResults': str(len(keywords))
        }
    }

    page = targeting_idea_service.get(selector)
    return_data = {}
    try:
        for result in page['entries']:
            attributes = {}
            for attribute in result['data']:
                attributes[attribute['key']] = getattr(attribute['value'], 'value', '0')
            # monthly search volume
            return_data[attributes['KEYWORD_TEXT']] = int(
                attributes['SEARCH_VOLUME'])
    except Exception as e:
        print e.__doc__
        print e.message
        pass
    return return_data




def get_estimate(country, language, data):
    """ data is a list of queries
    """
    final = {}
    error = []
    for i in xrange(0, len(data), 700):     
        kw = data[i:i+700]
        try:
            tmp = get_volume(kw, country, language) 
        except Exception as e:
            print e.message
            time.sleep(60)
            try:
                tmp = get_volume(kw, country, language) 
            except Exception as e:
                print e.message
                error.extend(kw)
                tmp = {}
                time.sleep(160)
        for k in tmp:
            final[k] = tmp[k]
    return final, error


# In[6]:


def get_estimate_recursive(country, language, data):
    """data is a list of queries
    """
    country = get_country_code(country)
    result_orig, error = get_estimate(country, language, data)
    while error:
        result, error = get_estimate(country, language, error)
        result_orig.update(result)
    return result_orig


# In[7]:


def process_result(result, filename):
    #convert result (dict) to dataframe
    df = pd.DataFrame(result.items(), columns=['keyword', 'volume'])
    #filter zero volume keywords
    df = df[df.volume>0]
    df.to_csv(filename, index=False)


# In[8]:


def get_data(filename):
    return pd.read_csv(filename, '\t', header=None, warn_bad_lines=True, error_bad_lines=False)


# In[9]:


def keyword_planner(filename, out, country_code, language):
    data = get_data(filename)
    queries = data[0].values.tolist()
    print len(queries)
    result = get_estimate_recursive(country_code, language, queries)
    process_result(result, out)


# In[10]:


keyword_planner('sample_keywords.txt', 'result.txt', 'US', 'English')

