'''20171117 extract data from dat/* files and create linear list'''
import os
import sys
from HTMLParser import HTMLParser

out_f = "results.csv"


def printf(s):
    m = s.strip()
    print m
    global out_f
    open(out_f, "a").write(m + "\n")

printf("id,title,name,org_code,org_unit,phone\n")
# ,cellular,address,email\n")


class MyHTMLParser(HTMLParser):

    # list the start tag and attributes
    def handle_starttag(self, tag, attrs):
        self.inLink = False
        ls_start.append([tag, attrs])

    # list the data after the start tag
    def handle_data(self, data):
        ls_data.append(data)


# set up a parser and feed it a file
def parse(f):
    parser = MyHTMLParser()
    parser.feed(f)


# need to remove magic number from here
for _id in range(0, 26003):
    # if(_id > 4261):
    # sys.exit(1)
    ls_start, ls_data = [], []
    name, title, phone, org_code, org_unit, mailing, cellular, email =\
        "", "", "", "", "", "", "", ""
    url = open("dat/" + str(_id) + "_u.txt").read().strip()
    words = url.split("&")
    for w in words:
        ws = w.split("=")
        if len(ws) == 2:
            if ws[0] == 'searchString':
                name = ws[1]

    name = name.replace("+", " ").strip().lower()

    # skip any records we can't parse a name from
    if name == "":
        continue

    f_dat = open("dat/" + str(_id) + "_d.txt").read()
    data_to_parse = (' '.join(f_dat.split())).strip().lower()
    parse(data_to_parse)

    last_data, last_last_data = "", ""

    for i in range(0, len(ls_start)):
        dat_str = str(ls_data[i]).strip().replace(",", ":")
        tg = ls_start[i][0].lower()

        # print "tag", str(ls_start[i][0]).strip(), "attrs",
        #   str(ls_start[i][1]).strip(), "data", str([dat_str])

        if tg in ["tr", "td", "img", "a", "table"]:
            if last_last_data == "telephone:":
                phone = dat_str
            elif last_last_data == "organization code:":
                org_code = dat_str
            elif last_last_data == "organization unit:":
                org_unit = dat_str
            elif last_last_data == name:
                title = dat_str
            elif last_data == "mailing address:":
                mailing = dat_str
            elif last_last_data == "cellular:":
                cellular = dat_str
            elif last_last_data == "email:":
                email = dat_str
            else:
                pass
            last_last_data = last_data
            last_data = dat_str

        if dat_str[0:18] == "scramble_addr_addr":
            # ["scramble_addr_addr('alcburnaby', 'gov.bc.ca', 'victoria1');"]
            ds = dat_str[18:]
            ds = ds.strip(";")
            ds = ds.strip("(")
            ds = ds.strip(")")
            words = ds.strip().split(",")
            for k in range(0, len(words)):
                words[k] = words[k].strip()
            for k in range(0, len(words)):
                words[k] = words[k].strip("'")
            for k in range(0, len(words)):
                words[k] = words[k].strip('"')
            for k in range(0, len(words)):
                words[k] = words[k].strip()
            # print words
            try:
                email = words[0] + "@" + words[2] + "." + words[1]
            except:
                pass
    phone = phone.strip()
    if phone == "not available":
        phone = ""
    out = ",".join([str(_id), str(title), str(name), str(org_code),
                    str(org_unit), str(phone) + "\n"])
    # "," + cellular + "," + mailing + "," + email + "\n"
    printf(out)
