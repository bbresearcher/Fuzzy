# Fuzzy is a fuzzing and sanity testing tool to fuzz and test code between Circom and Rust implementations.
Currently Fuzzy only supports the Poseidon hashing tests but could perhaps be extended

It consists of two components a `Flask` web admin panel and a python script for fuzzing which can be run from the command line.

![FrontPage](./images/frontpage.png)

and

![Fuzzy command line](./images/fuzzyhelp.png)

The functionality of the Web admin panel, allows users, to :
- Create tests
- Edit tests
- Delete tests
- Add test data for tests
- View test results

## Add/Edit
![addedit](./images/addedit.png)

## View tests
![View tests](./images/viewtests.png)

## View Test Results
This will show the actual outputs and if set can check if the outputs matched the expected output as set.

![View tests](./images/testresults.png)

## Run a SQL script to add or alter bulk data.
![RUN SQL](./images/runsql.png)

## Fuzzing commandline
The command line allows for 3 commadline arguments:
- `test_id` to run
- `number_of_fuzz_runs` to specify how many times to run
- `add_results_to_db` to specify if the results should be added to the `Flask` app database 0 for `no` and 1 for `yes`

**The example below run test number 1 for 3 runs and does not insert the results into the database**
![Fuzz run](./images/fuzzyrun.png)

## Installation:
To run this `Flask` app it is suggested to install `venv`.

`git clone https://github.com/bbresearcher/Fuzzy && cd ./Fuzzy`

Then run `source ./fuzzy/bin/activate`

Install `Flask` with `pip install flask`

Run the flass app with `python3 ./app.py`
