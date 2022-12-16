import datetime
from typing import Dict, List, Tuple
from pearls.client import make_client
from nlpy.client import NLClient
from pearls.app_env import AppEnv, get_app_env


def feature_import(ship_id,feature_name,sample_size):
    print("     |-> Importing data from features API...")
    #ship_id = 61
    #feature_name = 'SFOC'
    features_env = 'qa'

    __cfg__ = {
            AppEnv.LOCAL: {
                "apiurl": "http://localhost:8080",
                "autoloadlabels": True,
                "automigrate": True,
                "dbconfig": "host=localhost user=postgres password=postgres "
                            "dbname=postgres sslmode=disable",
                "dbtype": "postgres",
                "labels": "/labels/",
                "migrations": "/migrations/",
                "nlclient-email": "nautilus-api-user@nautiluslabs.co",
                "nlclient-password": "NaJRPwtzRMBjUf6b/B/2Eekm2SHHv3",
                "proxy": {"/proteus/": "http://localhost:5000"},
                "redis-client": "IN-MEMORY",
            },
            AppEnv.LOCAL_DOCKER: {
                "apiurl": "http://host.docker.internal:8080",
                "autoloadlabels": True,
                "automigrate": True,
                "dbconfig": "host=host.docker.internal user=postgres "
                            "password=postgres dbname=postgres sslmode=disable",
                "dbtype": "postgres",
                "labels": "/labels/",
                "migrations": "/migrations/",
                "nlclient-email": "nautilus-api-user@nautiluslabs.co",
                "nlclient-password": "NaJRPwtzRMBjUf6b/B/2Eekm2SHHv3",
                "proxy": {"/proteus/": "http://host.docker.internal:5000"},
                "redis-client": "IN-MEMORY",
            },
            AppEnv.QA: {
                "apiurl": "https://qa-api.nautiluslabs.co",
                "autoloadlabels": True,
                "automigrate": True,
                "dbconfig": "host=qa-db.nautilusinternal.com user=nluser "
                            "password=nluserpassword dbname=nldbqa",
                "dbtype": "postgres",
                "doorman-secret": "qa/doorman",
                "features-cache-s3prefix": "qa",
                "features-cache-s3writethrough": True,
                "ingesturl": "https://ingest-qa.nautiluslabs.co",
                "labels": "/labels/",
                "migrations": "/migrations/",
                "nl-support-email": "support@nautiluslabs.co",
                "nl-support-password": "l4OZmtIzI2YRSID3iji8eB2o4aU=",
                "nlclient-email": "nautilus-api-user@nautiluslabs.co",
                "nlclient-password": "NaJRPwtzRMBjUf6b/B/2Eekm2SHHv3",
                "persisted-records-topic": "arn:aws:sns:us-east-1:873656667372:persisted-records-qa",
                "persisted-samples-topic": "arn:aws:sns:us-east-1:873656667372:persisted-samples-qa",
                "proxy": {"/proteus/": "https://qa-proteus.nautiluslabs.co"},
                "redis-client": "redis:6379",
                "tethys-api": "https://gwhx7dv2l7.execute-api.us-east-1.amazonaws.com/qa",
                "tethys-key": "sOWYe1QoTF5rsF4qoyWKf85SC4JMlTTE8FXiRSg2",
            },

        }

    #config_and_status_file_name = get_google_sheets_file_name()
    #logger.info(f'getting config and status from {config_and_status_file_name}')
    #config_and_status, config_and_status_url = get_config_and_status(config_and_status_file_name)

    # for i in range(len(config_and_status)):
    #    config_and_status_row = config_and_status.iloc[i]
    #    ship_id = config_and_status_row['ship_id'].item()
    #    ship_name = config_and_status_row['ship_name']
    #    feature_name = config_and_status_row['feature']
    #    condition_name = config_and_status_row['condition']
    #    condition = conditions[condition_name]
    #    threshold = config_and_status_row['threshold'].item()
    #    slack_channel = config_and_status_row['alert_channel']
    #    status = config_and_status_row['status']

    #       env = get_app_env()
    # features_env = 'qa' if env == 'local' else env

    # env = get_app_env()
    print("Creating App Client...")
    nlclient = make_client(env=AppEnv(features_env))
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=sample_size)
    try:
        features: Dict[str, Dict[str, List]] = nlclient.get_features(ship_id, start_time, end_time)
    except Exception as e:
        error_message = f'⚠️\nenv: {features_env}\ncould not get features for ship {ship_id} {ship_name}: {e}'
        logger.error(error_message)
        # yield get_slack_notification(slack_channel, error_message)
        #continue
    print("     |-> SUCCESS!")
    print("     |-> Accessing Features API...")
    env=AppEnv(features_env)
    conf = __cfg__[env]
    c = NLClient(endpoint=conf["apiurl"])
    c.login(email=conf["nlclient-email"], password=conf["nlclient-password"])

    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=sample_size)
    try:
        features: Dict[str, Dict[str, List]] = nlclient.get_features(ship_id, start_time, end_time)
    except Exception as e:
        error_message = f'⚠️\nenv: {features_env}\ncould not get features for ship {ship_id} {ship_name}: {e}'
        logger.error(error_message)
        # yield get_slack_notification(slack_channel, error_message)
    #continue
    print("     |-> SUCCESS!")
    data_set = features

    matching_feature_name = None
    feature_data = []
    if feature_name in features['means']:
        matching_feature_name = feature_name
        feature_data = features['means'][feature_name]

    # if matching_feature_name is None:
    #    logger.error(f'no feature named {feature_name} found')
    # continue
    # logger.info(f'using feature named {matching_feature_name}', ship_id=ship_id, feature=feature_name, condition=condition_name, threshold=threshold, slack_channel=slack_channel)
    print("     |-> Features data capture Successful!")
    #   return(data_set)
    return data_set

