import requests
import jsonpickle

_errorHandler = None;
_host = 'localhost';
_port = 7000;

def initialize(host=None, port=None, errorHandler=None):
    '''
    Initialize logger and set configuration


    :param string   host:           HypnoLog server host name. Default is "localhost"
    :param int      port:           HypnoLog server port number. Default is 7000
    :param function errorHandler:   Function to handle when inner HypnoLog error occure. Of
                                    signature (error). If not given, default behavior will be used.
    '''
    global _host, _port, _errorHandler;
    if host != None:
        _host = host;
    if port != None:
        _port = port;
    if errorHandler != None:
        _errorHandler = errorHandler;

def log(obj, objType=None):
    '''
    Log given object using HypnoLog.

    :param object obj:      The object to be logged
    :param string objType:  String represent the type of the logged object, will determine how the
                            object is visualized. If not provided, `object` type will be used
    '''
    try:
        if objType == None:
            objType = _determineType(obj);

        # some const settings
        serverURL = 'http://{host}:{port}/logger/in'.format(host=_host, port=_port);

        # prase the log request in a valid HypnoLog-data object
        hypnologObj = { "data": obj, "type": objType };

        # encode the whole object to JSON
        postData = jsonpickle.encode(hypnologObj)

        # send the request to HypnoLog server
        r = requests.post(serverURL, headers={'Content-Type': 'application/json'}, data=postData);
        if r.status_code == 200:
            return True;

        # bad status code, raise exception
        raise Exception("Server response code is not 200. status code: {0}".format(r.status_code));

    except Exception as e:
        _onError(e);
        return False;

    return False;

def _onError(e):
    if _errorHandler != None:
        _errorHandler(e);
    else:
        print("HypnoLog error:\n{0}".format(e));
        # raise e;

def _determineType(obj):
    if isinstance(obj, str):
        return 'string';
    return 'object';

