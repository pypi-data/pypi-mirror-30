import httplib2, json, secrets

sandbox = "https://sandbox.hydrogenplatform.com/hydro/v1"
production = "https://api.hydrogenplatform.com/hydro/v1"

environment = "none"

# Define a function
def health():
    print("Hello, World!")

def setEnvironment(setter):
    if setter == "sandbox":
        environment = sandbox
        return environment
    elif setter == "production":
        environment = production
        return environment
    else:
        return "Please call this function with either 'sandbox' or 'production'"

def verify(username, password, user, message, application_id):
    if global environment == "none":
        return "Please set the environment variable"

    h = httplib2.Http(".cache")
    h.add_credentials(username, password)
    resp, content = h.request(environment + "/verify_signature?username="+user+"&msg="+message+"&application_id="+application_id,
        "GET",
        headers={'content-type':'application/json'} )

    resp_json = json.loads(content.decode("utf-8"))
    return(resp_json)

def addClientToApp(username, password, user, application_id):
    if environment == "none":
        return "Please set the environment variable"

    h = httplib2.Http(".cache")
    h.add_credentials(username, password)
    resp, content = h.request("https://dev.hydrogenplatform.com/hydro/v1/application/client?username="+user+"&application_id="+application_id,
        "POST",
        headers={'content-type':'application/json'} )

    resp_json = json.loads(content.decode("utf-8"))
    return(resp_json)

def generateMessage():
    code = str(secrets.randbelow(int(1e6))).zfill(6)
    return(code)

def whitelist(username, password, address):
    if global environment == "none":
        return "Please set the environment variable"

    h = httplib2.Http(".cache")
    h.add_credentials(username, password)
    resp, content = h.request("https://dev.hydrogenplatform.com/hydro/v1/whitelist/"+address,
        "GET",
        headers={'content-type':'application/json'} )

    resp_json = json.loads(content.decode("utf-8"))
    return(resp_json)

def challenge(username, password, hydroAddressId):
    if environment == "none":
        return "Please set the environment variable"

    h = httplib2.Http(".cache")
    h.add_credentials(username, password)
    resp, content = h.request("https://dev.hydrogenplatform.com/hydro/v1/challenge?hydro_address_id="+hydroAddressId,
        "GET",
        headers={'content-type':'application/json'} )

    resp_json = json.loads(content.decode("utf-8"))
    return(resp_json)

def authenticate(username, password, hydroAddressId):
    if environment == "none":
        return "Please set the environment variable"

    h = httplib2.Http(".cache")
    h.add_credentials(username, password)
    resp, content = h.request("https://dev.hydrogenplatform.com/hydro/v1/authenticate?hydro_address_id="+hydroAddressId,
        "GET",
        headers={'content-type':'application/json'} )

    resp_json = json.loads(content.decode("utf-8"))
    return(resp_json)
