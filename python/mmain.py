import json
import os
import psycopg
import base64
import requests
import gzip
import sys
import logging

mainUrl = "https://hackattic.com/challenges/backup_restore/%s?access_token=%s"


def getDbDump(token: str):
    """
    Getting source dump from hackattic.com
    """
    response = requests.get(url=f"{mainUrl}" % ("problem", token))
    return response.content


def postResult(token: str, ssnData: str):
    """
    Sending result to hackattic.com
    """
    return requests.post(url=f"{mainUrl}" % ("solve", token), data=ssnData)


def databaseConnector(sqlStatement: str, dbName: str, **connectionData):
    """
    This function allows to execute requests in database
    """
    try:
        logging.info('Trying to open connection to db')
        conn = psycopg.connect(
            user=connectionData['user'],
            password=connectionData['password'],
            dbname=dbName,
            host=connectionData['host'],
            autocommit=True
        )
        data = conn.execute(sqlStatement).fetchall()
        conn.close()
        return data
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    # Use position arguments
    listOfArgs = sys.argv
    dbUsername = listOfArgs[1]
    dbPassword = listOfArgs[2]
    dbHost = listOfArgs[3]
    accessToken = listOfArgs[4]

    # Database connection data
    defaultDbName = 'postgres'
    connData = {
        'user': dbUsername,
        'password': dbPassword,
        'host': dbHost
    }

    # Get, save and decompress database dump from source
    try:
        dump = json.loads(getDbDump(accessToken).decode('utf-8'))['dump']
        with open('dump.sql', 'w') as file:
            file.write(gzip.decompress(base64.b64decode(dump)).decode('utf-8'))
            file.close()
    except Exception as e:
        logging.error(e)
        exit(1)

    # Create new database
    tempDatabaseName = 'people_data'
    new_db = f'CREATE DATABASE {tempDatabaseName}'
    databaseConnector(new_db, defaultDbName, **connData)

    # Restore dump to new database
    logging.info("Restoring database dump")
    try:
        os.system(f"psql --dbname=postgresql://{connData['user']}:{connData['password']}"
                  f"@{connData['host']}:5432/{tempDatabaseName} < dump.sql")
    except Exception as e:
        logging.error(e)
    logging.info("Dump successfully restored")

    # Select appropriate values
    try:
        logging.info("Selecting values")
        ssnStatement = "select ssn from criminal_records where status like 'alive'"
        ssn = databaseConnector(ssnStatement, tempDatabaseName, **connData)
    except Exception as e:
        logging.error("FAILED to select data from database")
        logging.error(e)
        exit(1)
    logging.info("Data successfully selected")

    # Generate final list of social security numbers
    try:
        logging.info("Generating final list of social security numbers")
        final_list = []
        [final_list.append(i[0].strip()) for i in ssn]

        # Generate final dict and convert to json
        json_data = json.dumps({"alive_ssns": final_list})
    except Exception as e:
        logging.error("Generating list of social security numbers FAILED")
        logging.error(e)
        exit(1)

    # Sending request
    try:
        logging.info("Sending data")
        response = postResult(accessToken, json_data).content
    except Exception as e:
        logging.error("FAILED to sent data")
        logging.error(e)
        exit(1)

    # Store result to file
    try:
        logging.info("Storing result to file")
        with open("result/result.txt", "w") as result_file:
            result_file.write(str(response))
            result_file.write(json_data)
            result_file.close()
    except Exception as e:
        logging.error("FAILED to store result")
        logging.error(e)
        exit(1)
