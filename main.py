#!/usr/bin/env python
import argparse
import os
from datetime import datetime
from datetime import timedelta
from random import randint
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    """
    Main function to generate git commits for a specified date range.
    """
    args = arguments(def_args)
    curr_date = datetime.now()
    directory = 'repository-' + curr_date.strftime('%Y-%m-%d-%H-%M-%S')
    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email
    if repository is not None:
        start = repository.rfind('/') + 1
        end = repository.rfind('.')
        directory = repository[start:end]

    no_weekends = args.no_weekends
    frequency = args.frequency
    days_from = args.days_from
    days_to = args.days_to

    # --- Input Validation ---
    if days_from < 0:
        sys.exit('days_from must not be negative')
    if days_to < 0:
        sys.exit('days_to must not be negative')
    if days_from < days_to:
        sys.exit('days_from must be greater than or equal to days_to')

    # --- Repository Setup ---
    os.mkdir(directory)
    os.chdir(directory)
    run(['git', 'init', '-b', 'main'])

    if user_name is not None:
        run(['git', 'config', 'user.name', user_name])

    if user_email is not None:
        run(['git', 'config', 'user.email', user_email])

    # --- Commit Generation ---
    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days=days_from)
    number_of_days = days_from - days_to

    print(f"Generating commits from {days_from} days ago to {days_to} days ago...")

    for day_delta in range(number_of_days + 1):
        commit_date = start_date + timedelta(days=day_delta)
        # Check if commits should be made on this day
        if (not no_weekends or commit_date.weekday() < 5) and randint(0, 100) < frequency:
            # Create a random number of commits for the day
            for _ in range(contributions_per_day(args)):
                # Add a random number of minutes to the commit time
                commit_datetime = commit_date + timedelta(minutes=randint(0, 1439))
                contribute(commit_datetime)

    # --- Push to Remote Repository ---
    if repository is not None:
        run(['git', 'remote', 'add', 'origin', repository])
        run(['git', 'branch', '-M', 'main'])
        run(['git', 'push', '-u', 'origin', 'main'])

    print('\nRepository generation ' +
          '\x1b[6;30;42mcompleted successfully\x1b[0m!')


def contribute(date):
    """
    Creates a commit for a specific date.
    """
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date),
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands):
    """
    Executes a shell command.
    """
    Popen(commands).wait()


def message(date):
    """
    Generates a commit message based on the date.
    """
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    """
    Returns a random number of contributions for a day.
    """
    max_c = args.max_commits
    if max_c > 20:
        max_c = 20
    if max_c < 1:
        max_c = 1
    return randint(1, max_c)


def arguments(argsval):
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="A script to generate git commits for a specified date range.")
    parser.add_argument('-nw', '--no_weekends',
                        required=False, action='store_true', default=False,
                        help="Do not commit on weekends.")
    parser.add_argument('-mc', '--max_commits', type=int, default=10,
                        required=False, help="""Defines the maximum amount of
                        commits a day the script can make. Accepts a number
                        from 1 to 20. If N is specified the script commits
                        from 1 to N times a day. The exact number of commits
                        is defined randomly for each day. The default value
                        is 10.""")
    parser.add_argument('-fr', '--frequency', type=int, default=80,
                        required=False, help="""Percentage of days when the
                        script performs commits. If N is specified, the script
                        will commit N%% of days in the range. The default value
                        is 80.""")
    parser.add_argument('-r', '--repository', type=str, required=False,
                        help="""A link on an empty non-initialized remote git
                        repository. If specified, the script pushes the changes
                        to the repository. The link is accepted in SSH or HTTPS
                        format. For example: git@github.com:user/repo.git or
                        https://github.com/user/repo.git""")
    parser.add_argument('-un', '--user_name', type=str, required=False,
                        help="""Overrides user.name git config.
                        If not specified, the global config is used.""")
    parser.add_argument('-ue', '--user_email', type=str, required=False,
                        help="""Overrides user.email git config.
                        If not specified, the global config is used.""")
    parser.add_argument('-df', '--days_from', type=int, default=365,
                        required=False, help="""Specifies the start date for commits as days ago from today.
                        Default is 365.""")
    parser.add_argument('-dt', '--days_to', type=int, default=0,
                        required=False, help="""Specifies the end date for commits as days ago from today.
                        Default is 0.""")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
