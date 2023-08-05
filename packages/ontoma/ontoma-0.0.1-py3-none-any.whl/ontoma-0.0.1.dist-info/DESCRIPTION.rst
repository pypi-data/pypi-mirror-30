This software was developed as part of the Open Targets project. For more information please see:

http://www.opentargets.org
Target Validation platform

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.
Description: # OnToma
        
        ## Installing
        
        `pip install git+https://github.com/opentargets/OnToma.git`
        
        ## Usage
        
        We want:
        
        ```python
        from ontoma import find_efo
        
        print(find_efo('asthma'))
        
        #outputs:
        'EFO:000270'
        ```
        
        or the command line version
        
        ```sh
        ontoma -i <input_file> -o <output_dir>
        ```
        
        where input file is a file of diseases/traits in either codes or text
        
        ```txt
        ICD9:720
        asthma
        alzheimer's
        DO:124125
        ```
        
        # Developing
        
        ## set up your environment
        First clone this repo
        
        ```
        git clone https://github.com/opentargets/OnToma.git
        ```
        
        [Install pipenv](https://pipenv.readthedocs.io/en/latest/install/#homebrew-installation-of-pipenv) and then run
        ```sh
        pipenv install --dev
        ```
        to get all development dependencies installed. 
        
        Test everything is working:
        ```sh
        pipenv run pytest
        ```
        
        ## add a dependency with pipenv + setup.py
        To add a dep for a library, add it by hand to `setup.py`, then add it separately to Pipfile, so that it shows up both as a transitive dependency and in your locked dev environment
        
        ## Release to PyPi
        1. Once you are ready to cut a new release, update the version in setup.py and create a new git tag with git tag $VERSION.
        2. Once you push the tag to GitHub with git push --tags a new CircleCI build is triggered.
        3. You run a verification step to ensure that the git tag matches the version of ontoma that you added in step 1.
        4. CircleCI performs all tests.
        5. Once all of your test pass, you create a new Python package and upload it to PyPI using twine.
        
        ## TODO:
        
        - [ ] write a function that matches the query to the right lookup function
        - [ ] memoize/lru_cache the OBO/__init__ file requests
            https://docs.python.org/3/library/functools.html
            https://stackoverflow.com/questions/3012421/python-memoising-deferred-lookup-property-decorator
            https://stackoverflow.com/questions/17486104/python-lazy-loading-of-class-attributes
            https://stackoverflow.com/questions/14946264/python-lru-cache-decorator-per-instance
            singleton implementation at module level - defer loading
        
        
Keywords: opentargets ontology efo mapper
Platform: UNKNOWN
Classifier: Intended Audience :: Developers
Classifier: Operating System :: OS Independent
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.6
Classifier: Programming Language :: Python :: 3 :: Only
Requires-Python: >=3.2
