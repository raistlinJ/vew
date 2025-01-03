from rocketchat_API.rocketchat import RocketChat
import re
import sys, traceback
import csv 
import logging 
import os
import uuid
import time

def delete_user(logged_rocket, user):
    user_exists = logged_rocket.users_info(username=user).json().get("success")
    users_delete = None
    print("Attempting to delete user: " + str(user))
    if user_exists:
        user_id = (
            logged_rocket.users_info(username=user).json().get("user").get("_id")
        )
        users_delete = logged_rocket.users_delete(user_id).json()
    if users_delete != None and users_delete.get("success"):
        print("success")
        return True
    print("unsuccessful")
    return False

def delete_users(logged_rocket, user_list, ignore=[""]):
    results = []
    if isinstance(ignore, str):
        ignore = [ignore]
    for user in user_list:
        if user.lower() not in (string.lower() for string in ignore):
            results.append((user, delete_user(logged_rocket, user)))
    return results

def delete_all_users(logged_rocket, ignore=[""]):
    results = []
    if isinstance(ignore, str):
        ignore = [ignore]

    user_list = logged_rocket.users_list().json().get("users")

    for user in user_list:
        print("Working with user: " + str(user) + "\n")
        username = user.get("username")
        if username.lower() not in (string.lower() for string in ignore):
            results.append((username, delete_user(logged_rocket, username)))
    return results

def create_user(logged_rocket, username, password, email, name):
    print("Creating User: " + str(username))
    users_create = logged_rocket.users_create(
        email=email,
        name=name,
        password=password,
        username=username,
    ).json()
    if users_create.get("success"):# users_create.get("error")
        return True
    return False

def create_users(logged_rocket, user_pass_list, ignore=[""]):
    results = []
    if isinstance(ignore, str):
        ignore = [ignore]
    for (user, password) in users_passes:
        email = user+"@fake.com"
        name = user
        if name.lower() not in (string.lower() for string in ignore):
            results.append((user, create_user(logged_rocket, user, password, email, name)))
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
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        return None

def get_groups_fromfile(filename):
    logging.debug("get_groups_fromfile(): instantiated")
    #not efficient at all, but it's a quick lazy way to do it:
    answer = []
    i = 0
    try:
        if os.path.exists(filename) == False:
            logging.debug("get_groups_fromfile(): Filename: " + filename + " does not exists; returning")
            return None
        with open(filename) as infile:
            lines = infile.read().splitlines()
            for line in lines:
                answer.append([])
                for user in line.strip().split(","):
                    answer[i].append(user)
                i = i + 1
        return answer
    except Exception as e:
        logging.error("Error in get_groups_fromfile().")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(exc_traceback)
        #traceback.print_exception(exc_type, exc_value, exc_traceback)
        return None

def create_channel(logged_rocket, channel_name):
    name = channel_name
    channels_create = logged_rocket.channels_create(name).json()
    if channels_create.get("success"):
        return True
    return False

def delete_channel(logged_rocket, channel_name):
    channel_info = logged_rocket.channels_info(channel=channel_name).json()
    if channel_info != None and channel_info.get("success"):
        channel_id= channel_info.get("channel").get("_id")
        channels_delete = logged_rocket.channels_delete(room_id=channel_id).json()
        if channels_delete.get("success"):
            return True
    return False

def delete_all_channels(logged_rocket, ignore=["GENERAL", "general"]):
    results = []
    if isinstance(ignore, str):
        ignore = [ignore]
    channels_all = logged_rocket.channels_list().json()
    #print("ChANNELS_ALL: " + str(channels_all))
    if channels_all.get("success") != True:
        return False

    channels = channels_all.get("channels")
    for channel in channels:
        channel_name = channel.get("name")
        channel_id = channel.get("_id")
        #print("CURR WORKING: " + str(channel_name))
        if channel_name.lower() in (string.lower() for string in ignore):
            continue
        #channels_delete = logged_rocket.channels_delete(room_id=channel_id).json()
        results.append((channel_name, delete_channel(logged_rocket, channel_name)))

    return results

def add_all_to_channel(logged_rocket, channel_name):
    #get channel id first
    channel_info = logged_rocket.channels_info(channel=channel_name).json()
    if channel_info != None and channel_info.get("success"):
        channel_id= channel_info.get("channel").get("_id")
        channels_add_all = logged_rocket.channels_add_all(room_id=channel_id).json()
        if channels_add_all != None and channels_add_all.get("success"):
            return True
    return False

def add_im_from_to(logged_rocket, to_list):
    #unpack and create kwargs for inputs
    if not isinstance(to_list, list):
        logging.error("add_im_from_to(): " + str(to_list) + " is not a list")
        return False
    #ignore first element since it is the group name
    str_group = joined_string = ",".join(to_list[1:])
    
    im_create = logged_rocket.im_create_many(usernames=str_group).json()
    return im_create.get("success")

def add_ims_from_to(logged_rocket, groups_user_list):
    results = []
    
    if not isinstance(groups_user_list, list):
        logging.error("add_ims_from_to(): " + str(groups_user_list) + " is not a list")
        return False
    
    for to_list in groups_user_list:
        logging.debug("Calling add_im_from_to(): " + str(to_list))
        results.append((str(to_list),add_im_from_to(logged_rocket, to_list)))
    return results

##add functions to remove ims here


def add_group(logged_rocket, group_user_list, append_team_name="", add_members_all_teams=[]):
    if not isinstance(group_user_list, list):
        logging.error("add_group(): " + str(group_user_list) + " is not a list")
        return False
    if len(group_user_list) <= 0:
        logging.error("add_group(): " + str(group_user_list) + " no group name or users provided")
        return False
    name = group_user_list[0] + str(append_team_name)
    valid_name = re.sub(r'\W+', '', name)
    for add in add_members_all_teams:
        group_user_list.append(add)
    members = group_user_list[1:]
    valid_members = []
    for member in members:
        valid_members.append(re.sub(r'\W+', '', member))
    #members = ["jaharrison", "ncmenchaca"]
    print("Creating group: " + str(valid_name) + " MEMBERS: " + str(valid_members))
    group_make = logged_rocket.groups_create(name=valid_name,members=valid_members).json()
    return group_make.get("success")

def add_groups(logged_rocket, groups_user_list, append_team_name="", add_members_all_teams=[]):
    results = []
    
    if not isinstance(groups_user_list, list):
        logging.error("add_groups(): " + str(groups_user_list) + " is not a list")
        return False
    
    for group_list in groups_user_list:
        logging.debug("Calling add_groups(): " + str(group_list))
        results.append((str(group_list),add_group(logged_rocket, group_list, append_team_name, add_members_all_teams)))
    return results

def delete_group(logged_rocket, group_name, append_group_name=""):
    group_name = group_name + str(append_group_name)
    groups_delete = logged_rocket.groups_delete(group=group_name).json()
    if groups_delete.get("success"):
        return True
    return False

def delete_all_groups(logged_rocket, ignore=["GENERAL"]):
    results = []
    if isinstance(ignore, str):
        ignore = [ignore]
    groups_all = logged_rocket.groups_list_all().json()
    #print("GROUPS_ALL: " + str(groups_all))
    if groups_all.get("success") != True:
        return False

    groups = groups_all.get("groups")
    for group in groups:
        group_name = group.get("name")
        channel_id = group.get("_id")
        #print("CURR WORKING: " + str(group_name))
        if group_name.lower() in (string.lower() for string in ignore):
            continue
        #channels_delete = logged_rocket.channels_delete(room_id=channel_id).json()
        results.append((group_name, delete_group(logged_rocket, group_name)))

    return results


logged_rocket = RocketChat(sys.argv[1], sys.argv[2], server_url=sys.argv[3])
print("calling get_user_pass_fromfile()")
users_passes = get_user_pass_fromfile("users.csv")
print("FOUND USERS: " + str(users_passes))
#groups = get_groups_fromfile("groups_cs4177.txt")

#print("Got Users:" + str(users_passes))

print("Creating Users")
results = create_users(logged_rocket, users_passes)
print("User Creation Complete")
print("Results: ")
for result in results:
    print("Username: " + str(result[0]) + " " + str(result[1]))

print("waiting for 5 seconds...")
time.sleep(5)

# channel_name = "notifications"
# print("Creating Channel: " + str(channel_name))
# result = create_channel(logged_rocket, channel_name)
# print(result)
# print("Channel Creation Complete")

# channel_name = "general"
# print("Creating Channel: " + str(channel_name))
# result = create_channel(logged_rocket, channel_name)
# print(result)
# print("Channel Creation Complete")

# print("waiting for 5 seconds...")
# time.sleep(5)

channel_name="notifications"
print("Adding All Users to Channel: " + str(channel_name))
result = add_all_to_channel(logged_rocket, channel_name)
print(result)
print("Adding All to Channel Complete")

channel_name="general"
print("Adding All Users to Channel: " + str(channel_name))
result = add_all_to_channel(logged_rocket, channel_name)
print(result)
print("Adding All to Channel Complete")

print("waiting for 5 seconds...")
time.sleep(5)

#print("Creating IMs: " + str(groups))
# results = add_ims_from_to(logged_rocket, groups)
# print("Results: \n" + str(results))
# print("Creating IM Complete")

# print("waiting for 5 seconds...")
# time.sleep(5)

# print("Creating Groups: " + str(groups))
# results = add_groups(logged_rocket, groups, append_team_name="_toAdmins", add_members_all_teams=["username"])
# print("Create Groups Results: \n" + str(results))
# print("Creating Groups Complete")

# print("waiting for 5 seconds...")
# time.sleep(5)


# print("Removing All Groups: ")
# results = delete_all_groups(logged_rocket, ignore=["general", "notifications"])
# print("Removing Groups Results: \n" + str(results))
# print("Removing Groups Complete")

# print("waiting for 5 seconds...")
# time.sleep(5)

# print("Removing All Channels")
# result = delete_all_channels(logged_rocket, ignore=["general"])
# print(result)
# print("Remove Channels Complete")

# print("waiting for 5 seconds...")
# time.sleep(5)

# print("Removing All Users")
# results = delete_all_users(logged_rocket, ignore=["username", "username2", "username3", "username4", "username5"])
# print("Removing Completed")
# print("Results: ")
# for result in results:
#     print("Username: " + str(result))

# print("Removing Users" + str(users))
# users = [x[0] for x in users_passes]
# results = delete_users(logged_rocket, users, ignore=["username"])
# print("Removing Completed")
# print("Results: ")
# for result in results:
#     print("Username: " + str(result[0]) + " " + str(result[1]))

print("Done")