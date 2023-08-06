import logging
from watchdog import ContributorWatchdog
import sys


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description= "contributor watchdog for github project")
    parser.add_argument("--configfile", "-f", help = "config file for watchdog script")
    parser.add_argument("--logfile", "-F", help="log file for watchdog script", default=None)
    return parser.parse_args()


def check_input(var, name, type_convert=str):
    if str(var) == "":
        logging.error("{0} cannot be empty. Exiting !!".format(name))
        sys.exit(1)
    else:
        return type_convert(var)


def parse_config(configfile):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read(configfile)
    if "slack" not in config.sections() and "github" not in config.sections():
        logging.error("Missing slack or github section in config file!! Exiting")
        sys.exit(1)
    slack_token=check_input(config.get("slack","token"), "token in slack section")
    channel=check_input(config.get("slack", "channel"), "channel in slack section")
    github_token=check_input(config.get("github", "token"), "token in github section")
    project_name=check_input(config.get("github", "project"), "project in github section")
    polling_interval=check_input(config.get("github", "polling_interval"), "polling_interval in github section", int)
    return slack_token,channel,github_token,project_name,polling_interval

if __name__ == "__main__":
    args = parse_args()
    if args.logfile is None:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
        logging.info("log file not provided!! logging in console")
    else:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename=args.logfile, level=logging.INFO)

    configfile = args.configfile
    slack_token, channel, github_token, project_name, polling_interval = parse_config(configfile)

    watchdog = ContributorWatchdog(project_name=project_name, github_token=github_token)
    watchdog.watch_and_notify_in_slack(pollinginterval=polling_interval, slacktoken=slack_token,
                                       slackchannel=channel)

