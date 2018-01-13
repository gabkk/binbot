
infile = open("./credential", "r")
for line in infile.readline():
    print (line)
    if "SECRET" in line:
        print line
    elif "CLES" in line:
        print line
exit()
