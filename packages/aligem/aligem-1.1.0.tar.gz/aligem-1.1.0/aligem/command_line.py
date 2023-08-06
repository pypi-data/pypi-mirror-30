import jobs,token
import argparse
import subprocess
import os

def main() :
    ### top-level group (L0)
    parser = argparse.ArgumentParser(description="Welcome to AliGEM - ALICE Grid Enviroment Manager (https://github.com/vpacik/aligem)")
    parser.add_argument("-v","--verbose", help="produce verbose output", action="store_true")
    parser.add_argument("-d","--debug", help="debugging mode (additional printout)", action="store_true")
    parser.add_argument("--version", action="version", version='0.1', help="print current version")
    subparsers = parser.add_subparsers(title="operations",dest="command")

    ### sub-parsers
    # jobs parser (L1)
    parser_jobs = subparsers.add_parser("jobs", help="Grid jobs operations")
    jobs_subparsers = parser_jobs.add_subparsers(dest="job_command")

    # jobs sub-parsers (L2)
    jobs_subparser_status = jobs_subparsers.add_parser("status", description="Print out compact (colored) overview of jobs states:\n['USER'] #M(asterjob)/#S(ubjob) "+jobs.stateclr.ALL+"#ALL"+jobs.stateclr.ENDC+" ("+jobs.stateclr.DONE+"#DONE"+jobs.stateclr.ENDC+"|"+jobs.stateclr.RUNNING+"#RUNNING"+jobs.stateclr.ENDC+"|"+jobs.stateclr.ERROR+"#ERROR"+jobs.stateclr.ENDC+"|"+jobs.stateclr.REST+"#REST"+jobs.stateclr.ENDC+")", help = "print overview of currently registered grid jobs",formatter_class=argparse.RawTextHelpFormatter)
    jobs_subparser_status.add_argument("-u","--user", help="specify USER as CERN username",default=None)
    jobs_subparser_status.add_argument("-f","--full", help="print detailed overview of all jobs states (also invoked by --verbose)", action="store_true")
    jobs_subparser_status.add_argument("--only-positive", help="print only states with at least 1 (sub)job", action="store_true")

    jobs_subparser_kill = jobs_subparsers.add_parser("kill", help = "kill grid (sub)job(s) in DONE state")
    jobs_subparser_kill.add_argument("-r","--resub", help="resubmit failed jobs prior to sequential killing", action="store_true",dest="kill_resub")
    jobs_subparser_kill.add_argument("-A","--all", help="kill ALL registered jobs (independent of state)", action="store_true",dest="kill_all")
    # jobs_subparser_kill.add_argument("-u","--user", help="specify USER as CERN username")

    jobs_subparser_resubmit = jobs_subparsers.add_parser("resub", help = "re-submit all grid job(s) in ERROR, EXPIRED or ZOMBIE state")

    # token parser (L1)
    parser_token = subparsers.add_parser("token", help="AliEn token operations")
    token_subparsers = parser_token.add_subparsers(dest="token_command")
    token_subparser_init = token_subparsers.add_parser("init", help="Initialize new token")
    token_subparser_destroy = token_subparsers.add_parser("destroy", help="Destroy current token")
    token_subparser_info = token_subparsers.add_parser("info", help="List token information")

    args = parser.parse_args()
    args = vars(args) # make an dictionary out of namespace

    debug = args['debug']
    verbose = args['verbose']

    if debug :
        print "=== Arguments ================================="
        print args
        print "==============================================="

    # check if alien is within the $PATH
    if not check_alien(debug=debug) :
        print "AliEn not found in $PATH, please load alienv !"
        return

    if 'command' not in args :
        print "Something went wrong, no 'command' argument parsed."
        return

    if args['command'] == 'jobs' :
        if debug : print "inside jobs"

        if 'job_command' not in args :
            print "Something went wrong, no 'job_command' argument parsed."
            return

        # check for valid token (if not found, token-init)
        if (token.check() == False) :
            print "No valid token found. Initializiting new token!"
            token.init()

        local_user = jobs.exec_alien_cmd("alien_whoami")['output'].strip()

        if args['job_command'] == 'status' :
            if debug : print "inside status"

            if args['user'] is not None :
                local_user = args['user']

            if debug : print local_user
            if not verbose and args['full'] is True : verbose = True

            jobs.get_status(local_user, debug=debug, verbose=verbose,only_positive=args['only_positive'])

        if args['job_command'] == 'kill' :
            if debug : print "inside kill"
            # user = args.user

            if args['kill_all'] == True :
                if debug : print "kill all is ON!"
                jobs.kill_all(local_user, debug=debug)
            else :
                if debug : print "kill done only"
                jobs.kill_done(local_user,resub=args['kill_resub'], debug=debug)


        if args['job_command'] == 'resub' :
            if debug : print "inside resubmit"
            # user = args.user
            jobs.resubmit(local_user,debug=debug)


    if args['command'] == 'token' :
        if 'token_command' not in args :
            print "Something went wrong, no 'token_command' argument parsed."
            return

        if args['token_command'] == "init" :
            if not token.check() :
                token.init()
            else :
                print "Valid token already exists! Destroy it first!"

        if args['token_command'] == "destroy" :
            token.destroy()

        if args['token_command'] == "info" :
            token.info()
    return

def check_alien(debug=False) :
    """
    Check if AliEn commands are available (in $PATH)
    """
    if debug : print "check_alien()"
    path = os.getenv('PATH')

    if "/AliEn-Runtime/" not in path :
        return False

    return True
