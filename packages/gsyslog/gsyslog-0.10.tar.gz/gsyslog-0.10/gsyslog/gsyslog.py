#!/usr/bin/python

"""!
Using this module to start a debug log. At the top of a python script,
such as views.py put the following:
<code><pre>
    from gsyslog import gsyslog
    log = gsyslog.start_log("/var/log/vrdb2.log", "views")
</pre></code>
Instead of a print for debug purposes, use the log statement:
<code><pre>
    if debug: print("views/Search()")
    log.debug("views/Search()") # default info will not include debug
    log.setLevel(10) #20=info 10=debug
    log.debug("request.method(%s)", request.method)
</pre></code>
"""

import logging


def start_log(log_filespec=None, log_name="", log_level=logging.INFO):
    """start_log(log_filespec,log_name,log_level) to begin debug logging.
    An example to begin logging:
    <code><pre>
        log = gsyslog.start_log("/var/log/spam.log")
        log.debug("very low level, strictly debug build only")
        log.info("high level regular debug, retail build")
        log.warn("handled error of a non-fatal nature")
        # the following are serious and are also a printed to the screen
        log.error("errors unexpected, potential corruption")
        log.critical("The program is crashing, corruption has occurred.")
        log.exception("Unexpected exception")
    </pre></code>
    Further comment on style is to use parameter bounded by parens.
    For instace: log.debug("alpha(%s)"%str(alpha)). By bounding the
    %s with parens you can tell is there extra non-visible chars.
    Also using str(alpha) will convert the value to a string. If the type
    of alpha is not known it might cause a problem otherwise.
    @param log_filespec String default None, filespec of log file
    @param log_name String default "", name of the log instance
    @param log_level Int default debug, init level for log file
    @return instance of log object
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    add_name = ""  # type: str
    if log_name:
        add_name = " %(name)-6s"
    add_thread = ""  # type: str
    # if False:  # python filespec running, process&thred info
    #    add_thread = " %(pathname)s %(process)d/%(processName)s/" + \
    #                 "%(thread)d/%(threadName)s"
    # 2017-10-19 13:23:09,710 name   \path\py.py 1234/proc/123/main
    formatter = logging.Formatter(
        "%(asctime)s" + add_name + add_thread +
        " %(funcName)15s:%(lineno)-4d %(levelname)-8s %(message)s")
    # root/def/method: <module>:46 main:18 __init__:12
    if log_filespec:
        file_handler = logging.FileHandler(log_filespec)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)
    logger.info("===gsyslog.start_log(log_filespec='%s',log_name='%s'," +
                "log_level=%d)", log_filespec, log_name, log_level)
    return logger
