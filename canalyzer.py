### Made by Ethan Jackson and Kenneth Kowalski
### Jul 24, 2024

import json
import time
import os
import sys

# Arguments
n = len(sys.argv)

#Timing the execution of this program
start_time = time.time()

try:
    os.mkdir("Canalyzer-Outputs")
except:
    pass

try:
    os.chdir("Canalyzer-Outputs")
except:
    print("Something went wrong and python can't change directory into 'Canalyzer-Outputs', this may make a mess of your current directory... sorry.")
    pass

#Delete previous files to allow for new data to be written (Probably not the most efficient but I'm not a CS major)
try:
    os.remove("output.txt")
except:
    pass
try:
    os.remove("present.txt")
except:
    pass
try:
    os.remove("pgn.txt")
except:
    pass
try:
    os.remove("senttopgn.txt")
except:
    pass
try:
    os.remove("countofids.txt")
except:
    pass
try:
    os.remove("countofmessages.txt")
except:
    pass

#Open and create the output files
f = open("output.txt", "a")
p = open("pgn.txt", "a")
t = open("senttopgn.txt", "a")
h = open("countofids.txt", "a")
m = open("countofmessages.txt", "a")

print("--- Begin file output ---", file=f)

#Counting the amount of lines run through
COUNT = 0

#Lists to keep track of PGNs and device descriptions
presentPGN = []
presentDescription = []
hash = {}
hashm = {}
rememberData = None

#Now deal with arguments
i = 0
for arg in sys.argv:
    if arg == "-f":
        print("Data will be pulled from: ", sys.argv[i + 1])
        openfile = sys.argv[i + 1]

    if arg == "-p":
        #Testing to see if input will work or fail
        try:
            with open("caninfo.json", encoding="utf8") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            os.chdir('../')
            with open("caninfo.json", encoding="utf8") as json_file:
                data = json.load(json_file)
            os.chdir("Canalyzer-Outputs")
            #print(str(data[sys.argv[i + 1]]))
            if data[sys.argv[i + 1]] == None:
                print("PGN not found, pgn.txt and senttopgn.txt will be empty after the execution of this program.")
                print("The data sent from this PGN will be printed to pgn.txt, Data sent to this PGN will be printed to senttopgn.txt PGN:", sys.argv[i + 1])
                print("Messges sent with the PGN: ", sys.argv[i + 1], file=p)

        rememberData = sys.argv[i + 1]

    if arg == "-h":
        print("---- Help ----")
        print("The only arguments are -f and -p. -f will specify dump file, -p [PGN] to view both messages sent from the PGN and to the PGN's PDU Format")
        print("\nProgram ending...")
        exit() #Kill program
    
    #Keep track of which arg is being checked
    i += 1

def keepCount(hash, id):
    #print(hash)
    #Check for the ID in hash keys
    for key in hash.keys():
        if key == str(id):
            hash[str(key)] += 1
            return
    
    #Assign a position in the hash to the ID
    hash[str(id)] = 1


def parseinfo(line, data, COUNT, hash):
    #Parses lines into CANID and message send
    line = line.split(" ")
    newline = line[2].split("#")

    #Getting PGN from the CANID
    pgn = newline[0][2:6]

    try:
        if pgn == rememberData:
            print(newline[1] + "Sent to: " + newline[0][4:6] + "\n", file=p)
    except TypeError:
        pass

    try:
        if rememberData[0:2] == newline[0][4:6]:
            print(newline[1] + "from: " + newline[0] + "\n", file=t)
    except TypeError:
        pass

    keepTrack(presentPGN, pgn)
    keepCount(hash, newline[0].strip('\n'))
    keepCount(hashm, newline[1].strip('\n'))

    print("CAN ID: " + newline[0], file=f)

    print("Source: " + str(newline[0])[6:8], file=f)

    try:
        #Finding description of the PGN
        print("Description: " + data[pgn]["Description"], file=f)
        keepTrack(presentDescription, data[pgn]["Description"])
    except:
        #Catch case for PGNs not covered in the list
        if pgn[0] == "F" or pgn[0:2] == "1F":
            print("Unable to read PGN", file=f)
        else:
            #So this part was really confusing to me, I discovered that nibble 5 and 6 (counting from 1) were the destination address.
            #But since the PF (PDU Format) byte is what specifies the actual sensor cluster (except PDUs starting in F) we can search the JSON file as if it were, for instance, 0C00 instead of 0C01.
            try:
                print("Description: " + data[str(pgn[0:2]) + "00"]["Description"], file=f)
            except KeyError:
                print("Description Unavailable", file=f)

            try:
                keepTrack(presentDescription, data[str(pgn[0:2]) + "00"]["Description"])
            except KeyError:
                pass

    #binaryout = bin(int(str(newline[1]).strip('\n'), 16))[2:].zfill(len(str(newline[1]).strip('\n')) * 4)

    print("Message: " + newline[1].strip('\n'), file=f)
    #out = '.'.join(binaryout[i:i+8] for i in range(0, len(binaryout), 2))
    #print("Binary Message: " + out, file=f)
    print("\n", file=f)

def keepTrack(specifiedlist, PGN):
    for id in specifiedlist:
        if PGN == id:
            return
    specifiedlist.append(PGN)

#Attempting to open JSON file
try:
    with open("caninfo.json", encoding="utf8") as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    os.chdir('../')
    with open("caninfo.json", encoding="utf8") as json_file:
        data = json.load(json_file)
    os.chdir("Canalyzer-Outputs")



#Attempting to open TXT dump file, preferred use with Caring Caribou
try:
    file = open(openfile, 'r')
except FileNotFoundError:
    try:
        os.chdir("../")
        file = open(openfile, 'r')
    except FileNotFoundError:
        print("File not found, try again.")
        exit()

while True:
    #Read through each line and send to parseInfo()
    line = file.readline()
    COUNT = COUNT + 1

    if not line:
        break
    if line[0] == "#":
        #Passing through comments (Lines starting with #)
        pass
    else:
        parseinfo(line, data, COUNT, hash)
        #print(COUNT)

for pair in hash:
    print(str(pair) + " " + str(hash[pair]), file=h)

for pair in hashm:
    print(str(pair) + " " + str(hashm[pair]), file=m)

#Stopping timer
calltime = time.time() - start_time
f.close()
p.close()
t.close()
h.close()
m.close()

#Outputting list of present devices to new txt file
with open("present.txt", "a") as p:
    print(str(presentPGN), file=p)
    print(str(presentDescription), file=p)

print("Output sent to output.txt, devices present send to present.txt")
print("--- %s seconds ---" % (calltime))
print("Seconds per line (average): " + str(calltime/int(COUNT)))
