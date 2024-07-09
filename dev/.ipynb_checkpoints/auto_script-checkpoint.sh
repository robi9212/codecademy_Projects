#!/usr/local/bin/python3

#prompts the user to comfirm before cleaning the data
echo 'Ready to clean database? [1/0]'
read cleancontinue 

#if the user picks 1 then run the clean_data script 
if [ $cleancontinue -eq 1 ]
then 
    echo 'Cleaning database'
    python dev/script.py
    echo 'done cleaning database'

    #grab the first line of dev and prod changelogs
    dev_version=$( head -n 1 dev/changelog.md )
    prod_version=#( head -n 1 prod/changelog.md )

    #delimit the first line of the changelog by space
    read -a splitversion_dev <<< $dev_version
    read -a splitversion_prod <<< $prod_version

    #delimiting will result in a list of two elements
    #the second will contain the version numbers
    dev_version=${splitversion_dev[1]}
    prod_version=${splitversion_prod[1]}

    if [ $prod_version != $dev_version]
    #tell the user that the dev and prod changes are different
    #before moving on to dev files to prod ask 
    then
        echo 'New changes detected. move dev files to prod? [1/0]'
        read scriptcontinue
    else
        scriptcontinue=0
    fi
    #otherwise dont run 
else
    echo 'please come back when ready'
fi 

#if users select 1 then copy or move certain files from dev to prod
if [ scriptcontinue -eq 1 ]
then 
    for file in dev/*
    do
        if [ $file == 'dev/cleaned_cade.db'] || [ $file == 'dev/cleaned_cade.csv'] || [ $file == 'dev/changelog.md']
        then
            cp $file prod
            echo 'Copying' $file
        else
            echo 'not copying' $file
        fi
    done
    #otherwise dont run
else   
    echo 'please come back when ready'
fi