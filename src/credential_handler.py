import pathlib as pth
import json
from Luca.logger import LucaLogger
logger = LucaLogger(__name__)

#path to credential assets
PATH = pth.Path(__file__).parent.parent.absolute()
CREDENTIAL_PATH = PATH.joinpath("assets").joinpath("credentials")

#file names of credentials storage
FILES = {"SQUAREDLE": "squaredle.credentials.json", "TELEGRAM": "telegram.credentials.json"}
logger.debug("Available Services: {0}".format("".join(list(FILES.keys()))))

#services
SERVICES = {"SQUAREDLE":"login","TELEGRAM":"token"}

#input manager
def _correctinput(bot:str):
    """Check if inputted service is allowed"""
    if bot.upper() in SERVICES.keys():
        logger.debug("Input is a Service: {0}".format(bot))
        return SERVICES[bot]
    else:
        logger.debug("Input is not a Service: {0}".format(bot))
        return False
def _correctpath(bot:str):
    """Return path to requested credentials"""
    try:
        return CREDENTIAL_PATH.joinpath(FILES[bot.upper()])
    except:
        logger.error("Path to Credential unavailable", exc_info=True)
        return 0
def _correctdata(type:str, credentials):
    """Return correct login credentials for the service. Possible service types are 'login' (Email-Password) and 'token'"""
    if type == "login":
        logger.info("Login Info being registered: {0}".format(credentials["email"]))
        return {"email": credentials["email"], "password":credentials["password"]}
    elif type == "token":
        logger.info("Token Info being registered")
        return {"token": credentials["token"]}
    else:
        #raise Error
        logger.error("No Login Info Available", exc_info=True)
        return 0
def _correctupdate(type:str, credentials, old_credentials):
    """Return correct login credentials for the service with memory of old email or token. Possible service types are 'login' (Email-Password) and 'token'"""
    if type == "login":
        if len(credentials["email"]):
            logger.info("New email and password being registered: ".format(credentials["email"]))
            return {"email": credentials["email"],"password":credentials["password"],"old email":old_credentials["email"]}
        else:
            logger.info("New password being registered: ".format(old_credentials["email"]))
            return {"email": old_credentials["email"], "password": credentials["password"]}
    elif type == "token":
        logger.info("New Token being registered")
        return {"token": credentials["token"], "old token": old_credentials["token"]}
    else:
        #raise Error
        logger.error("No new information updated", exc_info=True)
        return 0

#register new credentials
def register(service:str, email = "", password = "", token = ""):
    """Register new login credentials for a service bot

    Args:
        service (str): Possible values: SQUAREDLE
                                        TELEGRAM
        email (str, optional): Register email address if pertinent. Defaults to "".
        password (str, optional): Register password if pertinent. Defaults to "".
        token (str, optional): Register token if pertinent. Defaults to "".

    Returns:
        _type_: _description_
    """
    credentials = {"email":email,"password":password,"token":token}
    service_type = _correctinput(service)
    if service_type:
        data = _correctdata(service_type, credentials)
        with open(_correctpath(service),"w") as f:
            try:
                json.dump(data, f)
            except:
                logger.error("Registration of json credentials was unsuccesful",exc_info=True)
    else:
        #raise Error
        return 0

#update credentials
def update(service:str, email = "", password = "", token = ""):
    """Update the login credentials for a service bot

    Args:
        service (str): Possible values: SQUAREDLE
                                        TELEGRAM
        email (str, optional): Update email address, if left empty, won't update. Old email will be kept to memory. Defaults to "".
        password (str, optional): Update password. Defaults to "".
        token (str, optional): Update token. Defaults to "".

    Returns:
        _type_: _description_
    """
    credentials = {"email":email,"password":password,"token":token}
    service_type = _correctinput(service)
    if service_type and (len(password) or len(token)):
        old_data = getcredentials(service) #get old logins
        data = _correctupdate(service_type, credentials, old_data)
        with open(_correctpath(service),"w") as f:
            try:
                json.dump(data, f)
            except:
                logger.error("Update of credentials was unsuccessful", exc_info=True)
    else:
        #raise Error
        return 0

#retrieve credentials
def getcredentials(service:str):
    """Get the credentials

    Args:
        service (str): Possible values:     SQUAREDLE
                                            TELEGRAM
    """
    if _correctinput(service):
        with open(_correctpath(service),"r") as f:
            try:
                return json.load(f)
            except:
                logger.error("Crendials not available", exc_info=True)
                return 0
    else:
        #raise Error
        return 0
