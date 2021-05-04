import os, json

fp = open("./rid.json", 'r')
jdata = json.load(fp)
fp.close()


with open("./new.md", 'w') as md:
    md.write("| Parameters | Type | Description | Default/Example |\n")
    md.write("| :----: | :----: | :----: | :----: |\n")
    for ii in jdata:
        md.write("| {} | * | * | {} |\n".format(ii, jdata[ii]))