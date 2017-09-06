# kwplanner
Keyword planner using Google Adwords API


## How to use
1) Clone the repo
```
git clone git@github.com:iamaris/kwplanner.git
```

2) Install the required packages
```
cd kwplanner
pip install -r requirements.txt
```

3) Place the credentials file (auth.yaml) in your home directory. The script assumes that the file is named ```auth.yaml``` and is located in the home directory. You can use a different name and location but you have to input that information every time you run the script.


4) Run the program. For example, you want to check the __US__ volume estimates of the __English__ keywords in a file named __keywords.txt__ and located in your home directory. This also assumes that you did step 3.
```
python kwplanner -country_code US -language English -keyword_file ~/keywords.txt 
```

The result will be saved inside the ```kwplanner``` folder.

```
Extra parameters:
  -output_name  OUTPUT_NAME    : OUTPUT_NAME is the name and location of the output file. For example: ~/out.txt

  -auth_file AUTH_FILE         : AUTH_FILE is the location of the file that contains the credential  information. 
                                 By default it is ~/auth.yaml.
  -sleep_duration SLEEP_DURATION      : SLEEP_DURATION is the sleep duration (in seconds) everytime the API call
                                        rate limit is exceeded. The default value is 60. The minimum value should be 30.
  -max_kw MAX_KW        : MAX_KW is the maximum number of keywords per API call. Default value is 700.
  -show_languages       : Add this if you want to see all the possible languages.
  -show_countries       : Add this if you want to see all the possible countries.
  -test                 : Add this to run a test.
```

