#!/usr/bin/python
import argparse
from googleads import adwords
import json
import pandas as pd
from datetime import datetime
import time


__author__ = "aris"
__license__ = "MIT License"
__version__ = "0.9.1"

class keyword_planner(object):
    def __init__(self,
                 country_code='US', 
                 language='English',
                 keyword_file='./conf/sample_keywords.txt', 
                 output_name=None,  
                 auth_file='~/auth.yaml', 
                 sleep_duration=60,
                 max_number_of_keywords=700):
        self._client = adwords.AdWordsClient.LoadFromStorage(auth_file)
        self._country_code = country_code
        self._language = language
        self._keyword_file = keyword_file
        self._output_name = output_name or 'result_'+str(datetime.now()).replace(' ','_')+'.txt'
        self._sleep_duration = sleep_duration
        self._max_number_of_keywords = max_number_of_keywords

    def get_version(self):
        with open('./conf/version.json', 'r') as readfile:
            data = json.load(readfile)
        return data["version"]

    def get_language_code(self, language):
        with open('./conf/languagecodes.json', 'r') as readfile:
            lang = json.load(readfile)
            return lang[language]
        
    def get_country_id(self, country_code):
        cn = pd.read_csv('./conf/countries.csv')
        cn = cn.fillna('NA') # Namibia is read as NaN by pandas
        cn.set_index('Country Code', inplace=True)
        return cn['Criteria ID'][country_code.upper()]
    
    def get_volume(self, keywords):
        """ keywords is a list of keywords """

        keywords = list(filter(None, keywords))
        language_code = self.get_language_code(self._language)
        country_id = self.get_country_id(self._country_code)
        targeting_idea_service = self._client.GetService('TargetingIdeaService', version=self.get_version())

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
                'locations': [{'id': country_id}]
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
        for result in page['entries']:
            data = result['data']
            return_data[data[0]['value']['value']] = int(data[1]['value']['value'] or 0)
        return return_data
    


    def get_estimate(self, data):
        """ data is a list of queries
        """
        final = {}
        error = []
        for i in range(0, len(data), self._max_number_of_keywords):     
            kw = data[i:i+self._max_number_of_keywords]
            try:
                tmp = self.get_volume(kw) 
            except Exception as e:
                print(e)
                time.sleep(self._sleep_duration)
                try:
                    tmp = self.get_volume(kw) 
                except Exception as e:
                    print(e)
                    error.extend(kw)
                    tmp = {}
                    time.sleep(self._sleep_duration)
            for k in tmp:
                final[k] = tmp[k]
        return final, error
    
    def get_estimate_recursive(self, data):
        """data is a list of queries
        """
        result_orig, error = self.get_estimate(data)
        while error:
            result, error = self.get_estimate(error)
            result_orig.update(result)
        return result_orig
    
    def process_result(self, result):
        #convert result (dict) to dataframe
        df = pd.DataFrame(result.items(), columns=['keyword', 'volume'])
        #filter zero volume keywords
        df = df[df.volume>0]
        df.to_csv(self._output_name, index=False)
        
    def get_data(self):
        return pd.read_csv(self._keyword_file, '\t', encoding = 'utf8', header=None, warn_bad_lines=True, error_bad_lines=False)
    
    def run(self):
        data = self.get_data()
        queries = data[0].values.tolist()
        print('Number of keywords to process: ', len(queries))
        result = self.get_estimate_recursive(queries)
        self.process_result(result)
        print('Done! Output saved as {0}'.format(self._output_name))



def main():
    cn = pd.read_csv('./conf/countries.csv')
    cn = cn.fillna('NA')
    cn.set_index('Country Code', inplace=True)
    countries = list(cn.index) 

    with open('./conf/languagecodes.json', 'r') as readfile:
        languages = json.load(readfile)

    """Get arguments from command line"""
    description_text = """
    Pull keyword (query) montly volume estimate using Google Adwords TargetingIdeaService.
    """
    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument('-country_code', default='US', choices=countries, 
                        help='Two letter country code. For example: JP for Japan, GB for United Kingdom, etc. The default value is US.')
    parser.add_argument('-language', default='English', choices=languages, help='Language spelled out. The default value is English')
    parser.add_argument('-keyword_file', default='./conf/sample_keywords.txt', help='Location of the file that contains the keywords.')
    parser.add_argument('-output_name', help='Filename of the output file.')
    parser.add_argument('-auth_file', default='~/auth.yaml', help='The location of the file that contains the credential information. By default it is ~/auth.yaml.')
    parser.add_argument('-sleep_duration', default=60, help='Sleep duration (in seconds) everytime the API call rate limit is exceeded. The default value is 60. The minimum value should be 30.')
    parser.add_argument('-max_kw', default=700, help='The maximum number of keywords per API call. Default value is 700.')
    parser.add_argument('-show_languages', action='store_true')
    parser.add_argument('-show_countries', action='store_true')
    parser.add_argument('-test', action='store_true')
    args = parser.parse_args()

    if args.show_languages:
        for i in sorted(languages):
            print (str(i), languages[i])

    if args.show_countries:
        country_dict = cn['Name'].to_dict()
        for i in sorted(country_dict):
            print(i, country_dict[i])

   
    kw = keyword_planner(country_code=args.country_code,
                         language=args.language,
                         keyword_file=args.keyword_file,
                         output_name=args.output_name,                          
                         auth_file=args.auth_file,  
                         sleep_duration=args.sleep_duration,
                         max_number_of_keywords=args.max_kw)
    
    if args.test:
        print('################################################')
        print('Parameters:')
        print(', '.join("%s: %s" % i for i in vars(kw).items()))
        print('################################################')
        print('Running test:')
        print(kw.get_volume(['rock&roll', 'indeed', 'jobs', 'niño']))
        print('################################################')
    else:
        kw.run()


if __name__ == '__main__':
    main()
