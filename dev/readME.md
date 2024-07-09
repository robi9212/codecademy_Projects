
Subscriber Cancellation Pipeline

Project Description 

Overview:
    - This is a mock database of long-term cancelled subscribers for a fictional subscription company, this database is regulary updated from multiple souces and needs to be cleaned routinely and trasnformed into usable shape with as little human intervention as possible

* Purpose: 
    - To build a data engineering pipeline to regularly transform a messy database into clean source of truth for any analitics team

* Goal: to build a semi automated pipeline
    - to perform unit tests to confirm data is accuate and clean
    - writes human-readable errors to an error log
    - checks and updates changelog automatically
    - production database is updated with new clean data


Folder Structrue
* dev/ : development directory
    - changelog.md : changelog files to track updates to the database
    - cademycode.db: orgional database contains raw data from the 3 tables(cademycode_students, cademycode_courses, cademycode_student_jobs)
    - cleaned_cade.db : cleaned database
        - contains 2 tables: missing_data and cleaned_cade

* prod/: production directory
    - changelog: script.sh will copy from /dev when updates are approved
    - cleaned_cade.db: script.sh will copy from /dev when updates are approved
    - cleaned_cade.csv: aggragated data in csv format for production use
- 

* writeup/:
    - clean_cade_data1.ipynb: jupyter notbook contianing the process of the discovery phase of this project

Python script
* mr.clean.py : python script for updating and cleaning the database

Base Script
* automation_script.sh: bash script to handle runing the python script and copying updated files from dev to prod directory

Instructions 
* ensure you have required packages installed(python, pandas, numpy)
* navigate to projects root dirctory
* run script.sh and follow the prompts to update the database
* if clean_data.py*** runs into any erros during unit test it will raise an excrption, log the error and terminate
* after succesfully updating, the numver of records and other update data will be written into dev/changelog.md
* script.sh will check the changelog to see if there are updates, if so it will request permission to overwrie the prodction database
