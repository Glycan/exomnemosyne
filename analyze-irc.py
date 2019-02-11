from collections import defaultdict, Counter
from pdb import pm, set_trace

"draw social graphs"
class User:
    def __init__(self, nick):
        self.nick = nick
        self.mentions = []
        self.messages = 1 # user is only made after reading a message
        
    def add_mention(self, mention):
        self.mentions[mention] += 1
    
    def __str__(self):
        return self.nick
    
    def __repr__(self):
        return "<{}, {} messages>".format(self.nick, self.messages)


class Analyse:
    def __init__(self, f):
        self.lines = f
        s = User("sylvie")
        self.users = [s]
        self.nicks = {"sylvie":s, "technillogue":s, "techn1llogue":s}
    
    def collect_nicks(self):
        parsed_lines = []
        for line in self.lines:
            # 19:21 < dx> edef: hi i'm inside you
            if line[6] == "<":
                nick, line = line[8:].split(">", 1)
                if nick not in self.nicks:
                    self.nicks[nick] = User(nick)
                    self.users.append(self.nicks[nick])
                else:
                    self.nicks[nick].messages += 1
                parsed_lines.append((nick, line))
            if " is now known as " in line:
                # 07:20 -!- puck1pedia is now known as puckipedia
                old, new = line[10:-1].split(" is now known as ") 
                if old in self.nicks:
                    user = self.nicks[old]
                    user.nick = new
                    self.nicks[new] = user
        return parsed_lines
    
    def collect_mentions(self, parsed_lines):
        nicks = self.nicks.keys()
        for nick, line in parsed_lines:
            mentions = self.nicks[nick].mentions
            [mentions.append(self.nicks[nick].nick)
            for nick in nicks if nick in line]
        
    def count_mentions(self):
        for user in self.users:
            count = Counter(user.mentions)
            total = sum(count.values())
            if total:
                user.mentions = [
                    (mention, value // total) 
                    for mention, value in count.most_common()
                ]
                

        
    def main(self):
        self.collect_mentions(self.collect_nicks())
        self.count_mentions()

with open("../logs") as f:
    a = Analyse(f)
    a.main()




        


