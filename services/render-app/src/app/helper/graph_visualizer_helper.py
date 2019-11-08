def generate_subPredObjList(g, prefixlist):
    subPredObjList = []
    for subj, pred, obj in g:
        subj = checkPrefixes(subj, prefixlist)
        pred = checkPrefixes(pred, prefixlist)
        obj = checkPrefixes(obj, prefixlist)

        # print(f"subj {subj}")
        # print(f"pred {pred}")
        # print(f"obj {obj}")

        subPredObjList.append(
            {"subject": str(subj), "predicate": str(pred), "object": str(obj)}
        )
    return subPredObjList


def generate_subPredObjList_from_TS(jsonResp, prefixlist):
    subPredObjList = []
    # print(jsonkResp)
    for elem in jsonResp["results"]["bindings"]:
        subj = checkPrefixes(elem["s"]["value"], prefixlist)
        pred = checkPrefixes(elem["p"]["value"], prefixlist)
        obj = checkPrefixes(elem["o"]["value"], prefixlist)

        # print(f"subj {subj}")
        # print(f"pred {pred}")
        # print(f"obj {obj}")

        subPredObjList.append(
            {"subject": str(subj), "predicate": str(pred), "object": str(obj)}
        )
    # print(subPredObjList)
    return subPredObjList


def generate_subPredObjList_forLists(g, prefixlist):
    subPredObjList = []
    index = 0
    subjold = None
    for subj, pred, obj in g:
        subj = checkPrefixes(subj, prefixlist)
        pred = checkPrefixes(pred, prefixlist)
        obj = checkPrefixes(obj, prefixlist)
        # to prevent showing and counting the names of the lists
        if not pred.startswith("N"):

            if subj == subjold:
                index += 1
            else:
                index = 0
                subjold = subj
            subPredObjList.append(
                {
                    "subject": str(subj),
                    "predicate": obj + " " + str(index),
                    "object": str(pred),
                }
            )
    return subPredObjList


def checkPrefixes(stringToCheck, prefixlist):

    split = stringToCheck.split("#")
    subjLong = split[0]
    found = False
    if len(split) > 1:
        for line in split:
            for namespace in prefixlist:
                if namespace["long"] in line:
                    subjLong = subjLong.replace(namespace["long"], namespace["short"])
                    found = True
                    break

        if found:
            stringToCheck = subjLong + split[1]

    else:
        stringToCheck = stringToCheck
    return stringToCheck


def generate_prefixlist_fromString(ttlstring):
    prefixlist = []
    lineList = ttlstring.split("\n")
    prefixString = "@prefix"
    for line in lineList:
        if prefixString in line:
            short = line.split()[1]
            longN = line.split()[2].split("<")[1].split("#")[0]

            prefixlist.append({"long": longN, "short": short})
        else:
            break
    return prefixlist

def generate_prefixlist_from_graph(geom_graph):

    rep = geom_graph["results"]["bindings"]
    prefix_list = []
    for i in rep:
        split_name = i["p"]["value"].split("#")
        entry ={ "long": split_name[0] , "short": split_name[-1] }
        if not entry in prefix_list:
            prefix_list.append(entry)
    return prefix_list

