#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
#    Jane - A helper bot for operation on Wikia wikis. 
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
import re

"""
Fallout - this file has been customized to meet the needs of Nukapedia.

The main purpose of this bot is to provide the chat staff with quick access
to policies and the Wikia Terms of Use. It also allows users to use a few 
other functions such as quick access to a desired users personal pages.
"""
class Jane(chatbot.ChatBot):

    """
    Sets the class variables and passes auth info to inherited chatbot functions.
    
    @param - username: The username of the bot to be used.
    @param - password: The password of the bot to be used.
    @param - wiki: The URL of the wiki to be logged in to.
    @param - tybot: Tybot class object for performing wiki tasks.
    """
    def __init__(self, username, password, wiki, tybot):
    
        #Tybot object
        self._tybot = tybot
        
        #Authorized users
        self._auth = [u'Lil\' Miss Rarity']
        
        #Sysops
        self._auth = self._auth + self._tybot.get_users_by_group("sysop")
        
        #Chat moderators
        self._auth = self._auth + self._tybot.get_users_by_group("chatmoderator")
        
        #Ignored users
        self._ignored = []
        
        #Pass authentication info to chatbot class
        chatbot.ChatBot.__init__(self, username, password, wiki)        
        
    """
    Prints a message upon connecting to chat with info about itself.
    
    @param - <all>: Passed automatically by chatbot module.
    """
    def on_welcome(self, c, e):
    
        #Message to be printed
        message = """Hello, I am Quality Control and I am here as a chat helper. I am a bot (automatic software). 
        A list of all of my availiable commands may be found on my userpage [[User:Quality Control|here]].
        """
        
        #Print welcome message into chat
        c.send(message)
        
    """
    Processes messages sent by users for commands and acts appropriately.
    
    @param - <all>: Passed automatically by chatbot module.
    """
    def on_message(self, c, e):
    
        #Check if a user is authourized
        if self._auth.count(e.user) >= 1:
        
            auth = True
            
        else:
        
            auth = False
            
        #Check the text for banned words
        if self._parse_swear(e.text) == True:
        
            c.send("Please do not use that word as it is forbidden, I suggest you read the [[Project:Chat|chat rules]].")
        
        #Make sure user is not ignored
        if self._ignored.count(e.user) != 1:
        
            #Commands - If a command takes input please create a class method for it's processing.
            
            #Lists location of commands
            if e.text.startswith("$commands"):
            
                c.send("[[User:Quality Control|Here is a list of my commands.]]")
                
            #Let me google that for you - calls method
            if e.text.startswith("$google"):
            
                #Call method "google it"
                self._google_it(e.text, e.user, c)
            
            #Simple test command
            if e.text.startswith("$test"):
            
                c.send("I am currently connected!")
                
            #Check if the user is authenticated
            if auth == True:
            
                #Reboots the bot
                if e.text.startswith("$die"):
                
                    c.send("/me takes the Enclave down with them.")
                    
                    sys.exit()
            
                #Ignore a user
                if e.text.startswith("$ignore "):
                
                    #Call method "ignore"
                    self._ignore(e.text, c)
            
                #Print links to users pages
                if e.text.startswith("$lookup"):
                
                    #Call method "lookup"
                    self._lookup(e.text, c)
            
                #Prints a link to the general site policies
                if e.text.startswith("$policy"):
                
                    c.send("Here is a link to Nukapædias [[Project:Policies and guidelines|policies and guidelines]]")
                 
                #Prints a link to the chat rules   
                if e.text.startswith("$rules"):
                
                    c.send("It is suggested that you read the [[Project:Chat|chat rules and guidelines]].")
                 
                #Prints a specific rule  
                if e.text.startswith("$rule "):
                
                    #Call method "print rule"
                    self._print_rule(e.text, c)
            
                #Prints a link to the Terms of Use
                if e.text.startswith("$tou"):
                
                    c.send("You seem to need a refresher and a link, here is the Wikia [[c:c:terms of use|Terms of Use]]")
                    
                #Unignore user
                if e.text.startswith("$unignore "):
                
                    #Call method "unignore"
                    self._unignore(e.text, c)
                
    """
    Prints a link to a google query
    
    @param - text: Text of message.
    @param - user: User who sent the message.
    @param - c: Class methods.
    """
    def _google_it(self, text, user, c):
    
        #Remove command
        cmd = text.replace("$google ", "")
        
        #Make sure there is a query
        if cmd == "":
        
            c.send("There is no query!")
            return
        
        #Replace spaces with "+"
        query_string = cmd.replace(" ", "+")
        
        #Build link
        link = "https://google.com/#q=" + query_string
        
        #Print link
        c.send("Here you go " + user +": " + link)     
        
    """
    Ignore a user
    
    @param - text: Message text
    @param - c: Class methods.
    """
    def _ignore(self, text, c):
        
        #Get user to ignore
        user = text.replace("$ignore ", "")
        
        #Make sure they aren't authenticated        
        if self._auth.count(user) >= 1:
            
            #Send error        
            c.send(user + " can not be ignored.")
            return
            
        elif self._ignored.count(user) == 1:
           
           #Print error             
           c.send(user + " is already being ignored.")
           return
           
        #Add user to ignore list
        self._ignored.append(user)
       
        #Send success
        c.send(user + " is now being ignored.")
        
    """
    Prints a link to a users userpage, talkpage, contributions.
    
    @param - text: The text content of the message.
    @param - c: Class methods.
    """
    def _lookup(self, text):
    
        #Remove command
        cmd = text.replace("$lookup ", "")
        
        #Make sure there is a query
        if cmd == "":
        
            c.send("No user specified!")
            return
        
        #Make links
        links = "[[User:" + cmd + "|User page]] - [[User talk:" + cmd + "|Talk page]] - [[Special:Contributions/" + cmd + "|Contributions]]"
        
        #Send links
        c.send(links)
        
    """
    Parses message to find banned words
    
    @param - text: Message to parse.
    
    @returns boolean
    """
    def _parse_swear(self, text):

        nigger = re.search(r"nig(ga|ger)", text, re.I)
        fag = re.search(r"fa(g|got)", text, re.I)

        if nigger or fag:

            return True

        else:

            return False
        
    """
    Prints a general summary of a rule and a link to the full chat rules.
    
    @param - text: Message text.
    @param - c: Class methods.
    """
    def _print_rule(self, text, c):
    
        #Get rule number (string)
        i = text.replace("$rule ", "")
        
        #Check if i is an int and not random text
        if i.isdigit():
            
            #Parse i into an integer        
            i = int(i) - 1

            #Check if i is in range
            if i > 9 or i < 0:

                #Print error and return
                c.send("No rule at this index!")
                return
            
            #List of rules        
            rules = [
                "[[Fallout Wiki:Chat#Chat_rules|No personal attacks, harassment, sexual harassment, insults or bullying.]]",
                "[[Fallout Wiki:Chat#Chat_rules|No racial bigotry, sexually degrading language, or other hate speech.]]",
                "[[Fallout Wiki:Chat#Chat_rules|Extreme use of profanity/cursing or directing it towards another user is not permitted.]]",
                "[[Fallout Wiki:Chat#Chat_rules|No violation of personal privacy.]]",
                "[[Fallout Wiki:Chat#Chat_rules|No linking to external sources, such as websites, which violate the aforementioned rules.]]",
                "[[Fallout Wiki:Chat#Chat_rules|No trolling or general irritation or disruption of other users.]]",
                "[[Fallout Wiki:Chat#Chat_rules|Don't be a dick.]]",
                "[[Fallout Wiki:Chat#Chat_rules|No whining.]]",
                "[[Fallout Wiki:Chat#Chat_rules|Be mindful when conversing of real world topics and know moderators carry the right to veto an topic.]]",
                "[[Fallout Wiki:Chat#Chat_rules|No spamming.]]"
            ]

            #Print requested rule
            c.send(rules[i])
            
        else:
            
            #Print an error        
            c.send(i + " is not a number.")
            
    """
    Remove a user from ignored list
    
    @param - text: Message to parse.
    @param - c: Class methods.
    """
    def _unignore(self, text, c):
    
        #Get user
        user = text.replace("$unignore ", "")
          
        #Checks if user was ignored        
        if self._ignored.count(user) == 1:
        
            #Removes user
            self._ignored.remove(user)
            
            #Prints success
            c.send("No longer ignoring " + user)
                    
        else:

            #Print error
            c.send("Wasn't ignoring " + user)
        
#Authentication details
username = sys.argv[1]
password = sys.argv[2]
subdomain = sys.argv[3]

#Site URL
wiki = "http://" + subdomain + ".wikia.com"
api = wiki + "/api.php"

#New Tybot object
tybot = tybot.tybot(username, password, api)

#Initialize Jane
if __name__ == "__main__":

    jane = Jane(username, password, wiki, tybot)
    jane.start()
