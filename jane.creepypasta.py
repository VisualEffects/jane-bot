#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
#    Jane - a sysop bot for Wikia wikis (Special:Chat)
#    Copyright (C) 2014  Benjamin Williams cataclysmicpinkiepie@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import tybot
import chatbot
import sys
import os
import datetime

"""
Chat logger
Takes messages passed to it and logs them in a file
"""
#Get number of logged lines
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
    
#Submit logs
def post_logs():

    #Generate date
    date = datetime.date.today()

    #Get current logs
    clogs = tybot.get_page_content("Project:Chat/Logs/" + str(date))
    
    logstart = "<pre>"
    logend = "</pre> [[Category:Chat logs]]"
    
    if clogs != "":
    
        logs = clogs.replace(logstart, "")
        logs = logs.replace(logend, "")
        
    else:
    
        logs = ""
        
    #Get logs from file
    f = open("logs.txt", "r")
    clogs = f.read()
    f.close()
    
    llogs = logstart + "" + logs + "" + clogs + "" + logend
    
    result = tybot.edit("Project:Chat/Logs/" + str(date), llogs, "Updating Logs")
    
    print str(result)
    
    #Reset logs
    os.remove("logs.txt")
    
#Log messages
def log_message(user, text, type):

    #Generate 24 hour timestamp
    time = str(datetime.datetime.utcnow()).split(" ")
    time = time[1].split(":", 2)
    time = time[0] + ":" + time[1]

    #Proccess messages depending on type
    if type == "message":

        message = time + " <" + user.encode("ascii", "ignore") + "> " + text.encode("ascii", "ignore") + "\n"

    if type == "kick":

        message = time + " *!* " + user[0].encode("ascii", "ignore") + " has kicked " + user[1].encode("ascii", "ignore") + " from chat *!*\n"

    if type == "ban":
    
        message = time + " *!* " + user[0].encode("ascii", "ignore") + " has banned " + user[1].encode("ascii", "ignore") + " from chat *!*\n"

    if type == "leave":
    
        message = time + " *!* " + user.encode("ascii", "ignore") + " has left Special:Chat *!*\n"

    if type == "join":
    
        message = time + " *!* " + user.encode("ascii", "ignore") + " has joined Special:Chat *!*\n"
    
    #Add message to log file
    f = open("logs.txt", "a")
    f.write(message)
    f.close()
    
    #Check to see if we can log
    if file_len("logs.txt") == 500:
    
        post_logs()

"""
Chat bot
This class contains all of the code needed to operate 
the chat aspect of the bot. It also calls functions
from Wiki comands
"""
class Jane(chatbot.ChatBot):

    def __init__(self, username, password, site, whitelist, tybot):

        #Login
        chatbot.ChatBot.__init__(self, username, password, site)

        #Set class variables
        self.whitelist = whitelist
        self.tybot = tybot
        
    def on_kick(self, c, e):
    
        #Log message
        log_message(e.user, e.text, "kick")
        
    def on_ban(self, c, e):
    
        #Log message
        log_message(e.user, e.text, "ban")
        
    def on_leave(self, c, e):
    
        #Log message
        log_message(e.user, e.text, "leave")
        
    def on_join(self, c, e):
    
        #Log message
        log_message(e.user, e.text, "join")

    def on_welcome(self, c, e):

        #Send welcome message
        c.send("Booting...")

    def on_message(self, c, e):
    
        """
        Log the message to file before processing
        """
        log_message(e.user, e.text, "message")
    
        """
        Commands for normal users
        """
        #Prints info on the bot for normal users
        if e.text.startswith("$info"):
        
            #Print info
            info = "Hello, I am Quality Control. I am a sysop bot and as such only take commands from users with sysop rights. I perform actions such as deleting pages and blocking users on command."
            
            c.send(info)

        """
        Sysop commands
        """
        if self.whitelist.count(e.user) == 1:
        
            #Test connection
            if e.text.startswith("$test"):
            
                #Print test
                c.send("Hello " + e.user)
                
            #Ban
            if e.text.startswith("$ban "):
            
                #Split variables
                cond = e.text.replace("$ban ", "")
                cond = cond.split(" > ")
                user = cond[0]
                time = cond[1]
                time = int(time) * 24 * 60 * 60
                reason = cond[2]
                
                c.ban_user(user, time, reason)
            
            #Block  
            if e.text.startswith("$block "):
            
                #Split into variables
                cond = e.text.replace("$block ", "")
                cond = cond.split(" > ")
                user = cond[0]
                reason = cond[1]
                expiry = cond[2]
                
                #Send block request
                result = self.tybot.block(user, reason, expiry)

                #Check result and print message
                if result == True:
                
                    c.send("Successfully blocked " + user + " for " + expiry)
                    
                else:
                
                    c.send("Error encountered when blocking " + user)
            
            #Delete
            if e.text.startswith("$delete "):
            
                #Split into variables
                cond = e.text.replace("$delete ", "")
                cond = cond.split(" > ")
                page = cond[0]
                reason = cond[1]
                
                #Send delete request
                result = self.tybot.delete(page, reason)
                
                #Check result and print message
                if result == True:
                
                    c.send("Page " + page + " was deleted.")
                    
                else:
                
                    c.send("Error enctountered when deleting page " + page)

            #Kick
            if e.text.startswith("$kick "):

                #Split into variables
                cond = e.text.replace("$kick ", "")

                #Kick
                c.kick_user(cond)
                    
            #Unblock
            if e.text.startswith("$unblock "):
            
                #Split into variables
                cond = e.text.replace("$unblock ", "")
                cond = cond.split(" > ")
                user = cond[0]
                reason = cond[1]
                
                #Send unblock request
                result = self.tybot.unblock(user, reason)
                
                #Check result and return message
                if result == True:
                
                    c.send("Unblocked " + user)
                    
                else:
                
                    c.send("Error encountered while unblocking " + user)
                    
            #Emergency quit
            if e.text.startswith("$die"):
            
                #Print exit message
                c.send("Emergency failsafe activated!")
                
                #Kill bot
                sys.exit()
              
            #Whitelist    
            if e.text.startswith("$whitelist ") and e.user == "Lil' Miss Rarity":
                
                #Split variables
                cond = e.text.replace("$whitelist ", "")
                
                #Check is already whitelisted
                if self.whitelist.count(cond) == 1:

                    c.send("User is already whitelisted.")

                else:

                    #Add to whitelist
                    self.whitelist.append(cond)
                
                    c.send("User " + cond + " has been whitelisted!")
                    
            if e.text.startswith("$updatelogs"):
            
                post_logs()
                
                c.send("Updating logs...")

"""
Setup
Gather login information and pass it
to the required class methods
"""
username = sys.argv[1]
password = sys.argv[2]
subdomain = sys.argv[3]

#Site URL
wiki = "http://" + subdomain + ".wikia.com"
api = wiki + "/api.php"

#New Tybot object
tybot = tybot.tybot(username, password, api)

#Get list of admins
whitelist = tybot.get_users_by_group("sysop")

#whitelisted users
whitelist.append("Lil' Miss Rarity")

#Start chatbot
if __name__ == "__main__":

    jane = Jane(username, password, wiki, whitelist, tybot)
    jane.start()
