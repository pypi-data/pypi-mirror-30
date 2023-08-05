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
Description: OnToma is a python module that helps you map your disease/phenotype terms to the
        ontology we use in the Open Targets platform.
        
        The ontology we use in the Open Targets platform is a subset (aka. _slim_) of
        the EFO ontology _plus_ any HPO terms for which a valid EFO mapping could
        not be found.
        
        
        *features*
        
        - Wrap OLS, OXO, Zooma in a pythonic API
        - Always tries to output full URI
        - Tries to find mappings iteratively using the faster methods first
        - Checks if mapping is in the subset of EFO that gets included in the
        Open Targets platform
        - *tries to* follow the procedure highlighted in https://github.com/opentargets/data_release/wiki/EFO-Ontology-Annotation-Process
        
        # Usage
        
        ## Installing
        
        `pip install ontoma`
        
        ## Quickstart
        
        Looking for a disease or phenotype string is simple:
        
        ```python
        from ontoma import OnToma
        
        otmap = OnToma()
        print(otmap.find_term('asthma'))
        
        #outputs:
        'http://www.ebi.ac.uk/efo/EFO_0000270'
        ```
        
        or the command line version:
        
        ```sh
        ontoma -i <input_file> -o <output_file>
        ```
        where input file can be replaced with `-` to read from stdin and write to stdout.
        
        For eg.
        ```sh
        echo 'asthma' | ontoma - test.txt
        ```
        
        will output a file `test.txt` containing the result, where it came from and the
        degree of confidence of the match (one of {match, fuzzy, check}):
        
        ```
        http://www.ebi.ac.uk/efo/EFO_0000270    EFO OBO     match
        ```
        
        
        More detailed documentation is at [![Documentation Status](https://readthedocs.org/projects/ontoma/badge/?version=latest)](http://ontoma.readthedocs.io/en/latest/?badge=latest)
        http://ontoma.readthedocs.io/en/stable/
        
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
        
        **if you don't like pipenv** you can stick with the more traditional
        setuptools/virtualenv setup:
        
        ```sh
        git clone https://github.com/opentargets/OnToma.git
        virtualenv -p python3 venv
        source venv/bin/activate
        pip install --editable .
        ```
        
        ## How to add a dependency
        
        **Add to both pipenv AND setup.py**
        
        To add a dep for a library, add it by hand to `setup.py`, then add it separately
        to `Pipfile`, so that it shows up both as a transitive dependency and in your
        locked dev environment
        
        ## Release to PyPi
        
        Simply run `./bumpversion.sh`
        
        The script will tag, push and trigger a new CI run.
        The package will be automatically uploaded to pypi.
        
Keywords: opentargets ontology efo mapper
Platform: UNKNOWN
Classifier: Intended Audience :: Developers
Classifier: Operating System :: OS Independent
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.6
Classifier: Programming Language :: Python :: 3 :: Only
Requires-Python: >=3.2
