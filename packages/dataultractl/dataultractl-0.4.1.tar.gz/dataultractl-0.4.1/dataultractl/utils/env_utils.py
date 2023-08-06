# -*- coding: utf-8 -*-
import os


def get_ttyclient_uri():
    ttyclient_uri = os.getenv("ADMINISTRATION_ENV_TTYCLIENT_URI", "http://10.131.40.20:9090/files/bin/bin.tar")
    return ttyclient_uri

