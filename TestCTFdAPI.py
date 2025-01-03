from plugins.ctfi2.api import API, dat, FILE_PATH, check_fields 
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
import logging
import sys, traceback
import csv
import os

def create_user(api_session, username, password, email="", email_ext="@fake.com", type="user", verified="false", hidden="false", banned="false", fields=[]):

    if email == "":
        email = username+str(email_ext)
    result = api_session.user_add(name=username, password=password, email=email, type=type, verified=verified, hidden=hidden, banned=banned, fields=fields)
    if result != {}:
        return True
    return False

def create_users(api_session, users_passes, ignore=[""]):
    results = []
    if isinstance(ignore, str):
        ignore = [ignore]
    for (user, password) in users_passes:
        name = user
        if name.lower() not in (string.lower() for string in ignore):
            results.append((user, create_user(api_session, user, password)))
    return results

def get_user_pass_fromfile(filename):
    logging.debug("get_user_pass_fromfile(): instantiated")
    #not efficient at all, but it's a quick lazy way to do it:
    answer = []
    i = 0
    try:
        if os.path.exists(filename) == False:
            logging.debug("get_user_pass_fromfile(): Filename: " + filename + " does not exists; returning")
            return None
        with open(filename) as infile:
            reader = csv.reader(infile, delimiter=" ")
            for user, password in reader:
                i = i+1
                answer.append((user, password))
        return answer
    except Exception as e:
        logging.error("Error in get_user_pass_fromfile().")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(exc_traceback)
        #traceback.print_exception(exc_type, exc_value, exc_traceback)
        return None


def get_teams_members(api_session):

    users = api_session.users_get()
    users_dict = {}
    print("Num Users: " + str(len(users)))
    for user in users:
        print("USER: " + str(user.get("name")) + " " + str(user.get("id")) )
        users_dict[user.get("id")] = user.get("name")

    teams_info = api_session.teams_get()
    teams_members_list = []
    print("Num Teams: " + str(len(teams_info)))
    #teams_info: [{'country': None, 'created': '2021-04-01T22:45:49+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 46, 'email': None, 'bracket': None, 'name': 'team5', 'fields': [], 'id': 12}, {'country': None, 'created': '2021-04-01T22:46:23+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 40, 'email': None, 'bracket': None, 'name': 'team6', 'fields': [], 'id': 13}, {'country': None, 'created': '2021-04-01T22:47:10+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 33, 'email': None, 'bracket': None, 'name': 'chompers', 'fields': [], 'id': 14}, {'country': None, 'created': '2021-04-01T22:47:22+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 34, 'email': None, 'bracket': None, 'name': 'BaconTeam', 'fields': [], 'id': 15}, {'country': None, 'created': '2021-04-01T22:47:38+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 42, 'email': None, 'bracket': None, 'name': 'team2', 'fields': [], 'id': 16}, {'country': None, 'created': '2021-04-01T22:48:06+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 44, 'email': None, 'bracket': None, 'name': 'Team 1', 'fields': [], 'id': 17}]
    for team_info in teams_info:
        #team_info: {'country': None, 'created': '2021-04-01T22:45:49+00:00', 'website': None, 'hidden': False, 'affiliation': None, 'banned': False, 'secret': None, 'oauth_id': None, 'captain_id': 46, 'email': None, 'bracket': None, 'name': 'team5', 'fields': [], 'id': 12}
        #print("TEAM: " + str(team_info.get("name")) + " ID: " + str(team_info.get("id")) )
        team_name = team_info.get("name")
        team_id = team_info.get("id")
        #team_all_info: [{'country': None, 'created': '2021-04-01T22:45:49+00:00', 'website': None, 'affiliation': None, 'banned': False, 'email': None, 'name': 'team5', 'fields': [], 'id': 12, 'members': [31, 46, 49], 'secret': None, 'oauth_id': None, 'bracket': None, 'hidden': False, 'captain_id': 46, 'place': '6th', 'score': 31}]
        team_all_info = api_session.team_get(team_info.get("id"))[0]
        #team_members: [1, 2, 3]
        team_members = team_all_info.get("members")
        #print("TEAM Members: " + str(team_members))
        #now get team name:
        team_members_list = [team_name]
        for member in team_members:
            #now add members by name
            #member: 31
            #print("MEMBER: " + str(member))
            if member not in users_dict:
                continue
            team_members_list.append(users_dict[member])
            #print("TEAM MEMBERS LIST: " + str(team_members_list))
        teams_members_list.append(team_members_list)
    return teams_members_list

def writeTeamMembersData(team_members_data, outfilename):
    logging.debug("writeFileData(): instantiated")
    try:
        with open(outfilename, 'w') as fd:
            for team in team_members_data:
                fd.write(', '.join(team))
                fd.write("\n")
        fd.close()
    except Exception:
        logging.error("Error in writeFileData(): An error occured ")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        return None


api_session = API(prefix_url=sys.argv[3])
api_session.login(sys.argv[1], sys.argv[2])

print("calling get_user_pass_fromfile()")
users_passes = get_user_pass_fromfile("g:\\My Drive\\work\\2024\\CTF3\\usersC_arl1.txt")

# #Add Users
print("ADDING USERS")
result = create_users(api_session, users_passes)
print("ADD USER RESULT: " + str(result))

#teams_members_list = get_teams_members(api_session)
#print("TEAM MEMBERS: " + str(teams_members_list))
#groups_filename = "groups.txt"
#print("Creating File: " + groups_filename)
#writeTeamMembersData(teams_members_list, groups_filename)
#print("Complete")
# result = api_session.user_get(31)
# print("USER 31: " + str(result) + "\n")

# result = api_session.team_get(12)
# print("TEAM 12: " + str(result) + "\n")
