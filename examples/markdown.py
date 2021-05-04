import os, json

fp = open("./rid.json", 'r')
jdata = json.load(fp)
fp.close()


with open("./new.md", 'w') as md:
    md.write("| parameters | description | default |\n")
    md.write("| :----: | :----: | :----: |\n")
    for ii in jdata:
        md.write("| {} | * | {} |\n".format(ii, jdata[ii]))