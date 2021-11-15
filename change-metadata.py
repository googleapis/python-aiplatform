import json

fname = ".repo-metadata.json"
rname = "README.rst"
ky = "client_documentation"
doc_link = ""
new_link = ""

new_data = {}

with open (fname) as jsonfile:
    data = json.load(jsonfile)
    doc_link = data[ky]
    product = doc_link.split("/")[4]
    data[ky] = new_link = f"https://cloud.google.com/python/docs/reference/{product}/latest"
    new_data = data

with open (fname, "w") as outfile:
    json.dump(new_data, outfile, indent=4)

with open (fname, "a") as outfile:
    outfile.write("\n")

content = ""
with open (rname, "r") as outfile:
    content = outfile.read().replace(doc_link, new_link)

with open (rname, "w") as outfile:
    outfile.write(content)

