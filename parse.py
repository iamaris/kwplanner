import argparse
import pandas as pd
import json

def main():
    cn = pd.read_csv('./countries.csv')
    cn = cn.fillna('NA')
    cn.set_index('Country Code', inplace=True)
    countries = list(cn.index) 
    print countries

    with open('./languagecodes.json', 'r') as readfile:
        languages = json.load(readfile)

    """Get arguments from command line"""
    description_text = """
    Pull keyword (query) montly volume estimate using Google Adwords TargetingIdeaService.
    """
    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument('-country_code', default='US', choices=countries, 
                        help='Two letter country code. For example: JP for Japan.')
    parser.add_argument('-language', default='English', choices=languages, help='Language spelled out.')
    parser.add_argument('-auth_file', default='~/auth.yaml')
    parser.add_argument('-sleep_duration', default=60)
    parser.add_argument('-max_kw', default=700, help='The maximum number of keywords per API call. Default value is 700.')
    parser.add_argument('-show_languages', action='store_true')
    parser.add_argument('-show_countries', action='store_true')
    args = parser.parse_args()

    print args

    if args.show_languages == True:
        for i in sorted(languages):
            print (i, languages[i])

main()
