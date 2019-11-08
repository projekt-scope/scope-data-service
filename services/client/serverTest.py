import json
import requests


proxies = {
    "http": None,
    "https": None,
}

def connectionTest(urlArr):
    """
    This function can print the error connection messages. The print statements are set deliberately because if an error is raised the other endpoints will not be checked.
    """

    noErrorRaisedUrl = ""

    for url in urlArr:
        try:
            requests.get(url)
        except requests.exceptions.RequestException as e:
            print('The url: %s raised the following exception(s):' % url, e)
        else:
            noErrorRaisedUrl = noErrorRaisedUrl + str(url) + " "

    if noErrorRaisedUrl != "":
        print("\n The url(s): %s aren't throwing errors" % noErrorRaisedUrl)
    else:
        pass


def sendTestJSON(testJSON):
    with open(testJSON) as f:
        try:
            json_file = json.load(f)

            # headers = {"Content-type": "application/json"}
            r = requests.post(
                'http://127.0.0.1:22633/revitAPI/fetchRevitData', json=json_file, proxies=proxies)
            print(r.status_code)

        except:
            print("Can't import the JSON data")
        

if __name__ == "__main__":
    urlArr = ['http://127.0.0.1:22630/', 'http://127.0.0.1:22631/',
              'http://127.0.0.1:22633/', 'http://127.0.0.1:22634/', 'http://127.0.0.1:22635/']
    connectionTest(urlArr)

    testJSON = "revit_export_example.json"
    sendTestJSON(testJSON)
