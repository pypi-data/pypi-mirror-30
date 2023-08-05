import google_trans

def translate(filename, src, tar, dest):
    with open("data/" + filename) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    out = open("data/" + dest, "w")
    for elt in content:
        if elt.startswith("```"): elt = elt
        elif elt.find("(") != -1 and elt.find(")") != -1:
            pause1 = elt.find("(")
            pause2 = elt.find(")")
            head = google_trans.api(elt[0:pause1], src, tar)
            tail = google_trans.api(elt[pause2+1:], src, tar)
            elt = head.encode('utf-8') + elt[pause1:pause2+1] + tail.encode('utf-8')
        else:
            elt = google_trans.api(elt, src, tar)
            elt = elt.encode('utf-8')
        out.write(elt)
        out.write("\n")
    out.close()

translate("output.md", "en", "hi", "translated2.md")
