#!/usr/bin/env python3

import os
import csv
import sys
from optparse import OptionParser


RESET = "\u001b[0m"
COLOR_RED = "\u001b[31m"
COLOR_BLUE = "\u001b[34m"
COLOR_YELLOW = "\u001b[33m"
COLOR_GREEN = "\u001b[32m"
UNDERLINE = "\u001b[4m"
BOLD = "\u001b[1m"

usage="""lpm.py [options]

 __    ____  ___  ___
 ||    || \\\ ||\\\//||
 ||    ||_// || \/ ||
 ||__| ||    ||    ||
"""

parser = OptionParser(usage=usage)
parser.add_option("-s", "--save", default=False, help=f"save {UNDERLINE}comma-separated{RESET} {BOLD}index{RESET}, {BOLD}id{RESET} and {BOLD}password{RESET} into the password file; For example: aws_login,user_aws_id,user_aws_password", action="store", type="string", dest="save_info")
parser.add_option("-g", "--get", default=False, help=f"finds and returns matching information using {UNDERLINE}index{RESET} in the password file.", action="store", type="string", dest="get_info")
parser.add_option("-d", "--delete", default=False, help=f"delete matching information using {UNDERLINE}index{RESET} in the password file", action="store", type="string", dest="delete_info")
parser.add_option("-l", "--list", default=False, help="list all the indexes that contain information.", action="store_true", dest="list_info")
(options, args) = parser.parse_args()

SAVE_INFO = options.save_info
GET_INFO = options.get_info
DELETE_INFO = options.delete_info
LIST_INFO = options.list_info

PASSWORD_FILE = os.environ['HOME'] + "/.password.csv"


def abort_if(condition, message):
    if condition:
        print(f"{COLOR_RED}Error{RESET}: ", message)
        exit(1)
    return

def check_valid_and_return(condition, string):
    info_array = string.split(',')

    abort_if((len(info_array) < condition or len(info_array) > condition),
        f"The Information must have {condition} elements")
    return info_array

def check_password_file_exist():
    file_exists = os.path.exists(PASSWORD_FILE)

    if not file_exists:
        print(f"{COLOR_YELLOW}Warning{RESET}: '.password.csv' is not found in your HOME directory.")
        if not create_password_file():
            return False
    return True


def create_password_file():
    choice = input("Do you want to create a new file in your HOME directory? [y/n] ").lower()

    if choice == 'y':
        filename = PASSWORD_FILE
        fields = ["Index", "Id", "Password"]

        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvfile.close()
        os.chmod(filename, 0o600)
        print(f"{COLOR_GREEN}Success{RESET}: '.password.csv' is created in your {COLOR_BLUE}{os.environ['HOME']}{RESET} directory!\n")
        return True
    else:
        return False

def check_duplicate_index(filename, info_array):
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        index = info_array[0]

        for row in csvreader:
            if row[0] == index:
                abort_if(True, "Duplicate index. Please use a different index.")
    return

def save_user_info(info_array):
    filename = PASSWORD_FILE
    index = info_array[0]

    check_duplicate_index(filename, info_array)
    with open(filename, 'a+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(info_array)
        csvfile.close()
    print(f"{COLOR_GREEN}Success{RESET}: Password has been saved to the following index: {index}")
    return

def get_user_info(info_array):
    filename = PASSWORD_FILE
    index = info_array[0]
    flag = False

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)

        for row in csvreader:
            try:
                base = row[0]
                if base == index:
                    flag = True
                    print(f"{COLOR_GREEN}Success{RESET}: The requested information is as follows:")
                    print(f"Index:      {row[0]}")
                    print(f"Id:         {row[1]}")
                    print(f"Password:   {row[2]}")
                    print("")
            except NameError as e:
                abort_if(True, e)
        csvfile.close()

    if not flag:
        print("No information found.\n")
    return

def delete_user_info(info_array):
    # making swap file
    current_filename = os.environ['HOME'] + '/.password.csv'
    to_old_filename = os.environ['HOME'] + '/.old_password.csv'
    try:
        os.rename(current_filename, to_old_filename)
        print(f"Historical informations has been saved to the following file in your HOME directory: {COLOR_YELLOW}'./old_password.csv'{RESET}")
        print("You can delete that file If you don't want,")
        print("")
    except:
        abort_if(True, "Failed to rename file. There is a problem with the system.")
    filename = current_filename

    flag = False
    index = info_array[0]
    with open(to_old_filename, 'r') as input_file, open(filename, 'w+') as output_file:
        csvwriter = csv.writer(output_file)
        csvreader = csv.reader(input_file)
        for row in csvreader:
            base = row[0]
            if base != index:
                csvwriter.writerow(row)
            else:
                flag = True
                print(f"{COLOR_GREEN}Success{RESET}: The following information is cleared.")
                print(f"Index: {row[0]}     Id: {row[1]}     Password: {row[2]}")
                print("")
        input_file.close()
        output_file.close()

    if not flag:
        print("Nothing to remove.\n")
    return

def list_index():
    filename = PASSWORD_FILE
    indexes = []

    try:
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader, None)

            for row in csvreader:
                indexes.append(row[0])
            csvfile.close()
    except:
        abort_if(True, "Cannot open password file.")
    indexes.sort()
    print("Indexes stored in password file:")
    print(*indexes, sep=", ")
    return

def main():
    info_array = []

    if SAVE_INFO:
        info_array = check_valid_and_return(3, SAVE_INFO)
        save_user_info(info_array)
    if GET_INFO:
        info_array = check_valid_and_return(1, GET_INFO)
        get_user_info(info_array)
    if DELETE_INFO:
        info_array = check_valid_and_return(1, DELETE_INFO)
        delete_user_info(info_array)
    if LIST_INFO:
        list_index()

if __name__ == "__main__":
    os.chmod("./lpm.py", 0o700)
    if check_password_file_exist():
        if len(args) > 0 or len(sys.argv) < 2:
            parser.print_help()
            exit(1)
        else:
            main()
            exit(0)
    else:
        print("\nProgram exits.\n")
        exit(1)
