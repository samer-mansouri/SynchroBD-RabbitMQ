import argparse
from subprocess import call
import sys
from dotenv import load_dotenv

load_dotenv()

def init_head_office():
    call(["python", "-m", "main.init_db.init_head_office"])

def init_branch_office_1():
    call(["python", "-m", "main.init_db.init_branch_office1"])
    
def init_branch_office_2():
    call(["python", "-m", "main.init_db.init_branch_office2"])

def branch_office_1():
    call(["python", "-m", "main.branch_offices.branch_office_1"])
    
def branch_office_2():
    call(["python", "-m", "main.branch_offices.branch_office_2"])
    
def head_office():
    call(["python", "-m", "main.head_office.head"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the project.")
    parser.add_argument('command', help='Subcommand to run')

    args = parser.parse_args()

    if args.command == "branch_office_1":
        branch_office_1()
    elif args.command == "branch_office_2":
        branch_office_2()
    elif args.command == "head_office":
        head_office()
    elif args.command == "init_head_office":
        init_head_office()
    elif args.command == "init_branch_office_1":
        init_branch_office_1()
    elif args.command == "init_branch_office_2":
        init_branch_office_2()
    else:
        print("Unknown command")
        sys.exit(1)