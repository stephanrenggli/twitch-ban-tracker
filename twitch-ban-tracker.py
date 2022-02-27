from twitchAPI.twitch import Twitch
import json
import os
import io
import time
import requests
import yaml
from rich import print
from rich.console import Console
from rich.panel import Panel

def load_config():
    with open("./storage/config.yml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        config_file.close()
    return config

def reload_tracked_accounts():
    with open("./storage/config.yml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    config_file.close()
    tracked_accounts = config['tracked_accounts']
    return tracked_accounts

def init_db(tracked_accounts, banned_accounts):
    if os.path.isfile('./storage/db.json') and os.access('./storage/db.json', os.R_OK):
        #print ("Database already exists...")
        return

    else:
        #print ("Initializing db...")
        with io.open(os.path.join('./storage/', 'db.json'), 'w') as db_file:
            db_file.write(json.dumps(
                {
                    'tracked_accounts': tracked_accounts,
                    'banned_accounts': banned_accounts
                }
            ))
            db_file.close()
        return

def update_db(tracked_accounts, banned_accounts):
    db_file = open('./storage/db.json')
    db_current = json.load(db_file)
    db_file.close()

    db_new = {
                    'tracked_accounts': tracked_accounts,
                    'banned_accounts': banned_accounts
                }

    if (db_current == db_new):
        #print('Nothing to do...')
        return
    else:
        #print('Updating database...')
        db_file = open('./storage/db.json', 'w')
        db_file.write(json.dumps(db_new))
        db_file.close()
    return

def get_banned_accounts(accounts):
    tracked_accounts = accounts
    tested_accounts = []
    banned_accounts = []

    request = twitch.get_users(logins=accounts)
    for i in request['data']:
        tested_accounts.append(i['login'])

    tracked = set(tracked_accounts)
    tested = set(tested_accounts)
    banned_accounts = list(sorted(tracked - tested))

    return banned_accounts

def get_changes(tracked_accounts, banned_accounts):
    current_tracked = tracked_accounts
    database_tracked = []
    new_tracked = []
    untracked = []

    current_banned = banned_accounts
    database_banned = []
    new_banned = []
    unbanned = []
    
    db_file = open('./storage/db.json')
    db_current = json.load(db_file)
    db_file.close()

    database_tracked = db_current['tracked_accounts']
    database_banned = db_current['banned_accounts']

    # current tracked
    current_tracked = set(current_tracked)

    # new tracked
    new_tracked = set(current_tracked) - set(database_tracked)

    # untracked
    untracked = set(database_tracked) - set(current_tracked)

    # current banned
    current_banned = set(current_banned)

    # new banned
    new_banned = set(current_banned) - set(database_banned)
    new_banned = new_banned - new_tracked # do not count as banned if newly tracked

    # unbanned
    unbanned = set(database_banned) - set(current_banned)
    unbanned = unbanned - untracked # do not count as unbanned if untracked

    return current_tracked, new_tracked, untracked, current_banned, new_banned, unbanned

def send_gotify_ban_notification(set):
    if len(set) > 0:
        for account in set:
            requests.post(f'{gotify_url}/message?token={gotify_token}', json={
                "title": "Twitch Ban Tracker",
                "priority": 2,
                "message": f'Account {account} was banned!'
            })

def send_gotify_unban_notification(set):
    if len(set) > 0:
        for account in set:
            requests.post(f'{gotify_url}/message?token={gotify_token}', json={
                "title": "Twitch Ban Tracker",
                "priority": 2,
                "message": f'Account {account} was unbanned!\nhttps://twitch.tv/{account}'
            })

def generate_summary(current_tracked, new_tracked, untracked, current_banned, new_banned, unbanned):
    
    console.print('[bold]The following accounts are being tracked:')
    for account in current_tracked:
        console.print(f':bust_in_silhouette:  {account}', style='blue')
    print()

    console.print('[bold]The following accounts are currently banned:')
    for account in current_banned:
        console.print(f':prohibited:  {account}', style='red')
    print()

    if len(new_tracked) > 0:
        console.print('[bold]The following accounts have been added:')
        for account in new_tracked:
            console.print(f':NEW_button:  {account}', style='cyan')
        print()

    if len(untracked) > 0:
        console.print('[bold]The following accounts are no longer being tracked:')
        for account in untracked:
            console.print(f':wastebasket:  {account}', style='dim')
        print()

    if len(new_banned) > 0:
        console.print('[bold]The following accounts have been banned:')
        for account in new_banned:
            console.print(f':police_car_light:  {account}', style='red')
        print()

    if len(unbanned) > 0:
        console.print('[bold]The following accounts have been unbanned:')
        for account in unbanned:
            console.print(f':heavy_check_mark:  {account}', style='green')
        print()

global tracked_accounts
config = load_config()

client_id = config['client_id']
client_secret = config['client_secret']
gotify_url = config['gotify_url']
gotify_token = config['gotify_token']
check_interval = config['check_interval']
tracked_accounts = config['tracked_accounts']

console = Console()
twitch = Twitch(client_id, client_secret)

print(Panel('Twitch Ban Tracker', style='bold purple'))

while True:
    console.log('Checking for changes...')
    print()
    tracked_accounts = reload_tracked_accounts()
    banned_accounts = get_banned_accounts(tracked_accounts)
    init_db(tracked_accounts, banned_accounts)
    get_changes(tracked_accounts, banned_accounts)
    current_tracked, new_tracked, untracked, current_banned, new_banned, unbanned = get_changes(tracked_accounts, banned_accounts)
    generate_summary(current_tracked, new_tracked, untracked, current_banned, new_banned, unbanned)
    send_gotify_ban_notification(new_banned)
    send_gotify_unban_notification(unbanned)
    update_db(tracked_accounts, banned_accounts)
    time.sleep(check_interval)