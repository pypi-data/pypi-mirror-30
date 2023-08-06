import os
import sys
import argparse
import dotmap
import logging

import utils
from utils import die

# -- read configuration file and merge in the provided options
# -- optDict : a dict with the initial options
# -- config  : dict or filename containing the configuration
# -- tag     : named section inside config to use in merging
# -- sections: name of the top level element of the config dict
# -- configs : list of configuration files
# -- returns a new dict, the result of merge of optDict and config dict
def merge(optDict,config=None,tag="default",sectionsName="sections",configs=[]):
    rdict = optDict
    cdict = None

    # -- if no configuration is specified, look for one in configs
    if config == None or config == "" : 
	for f in configs:
	    path=os.path.expanduser(f)
	    if os.path.exists(path):
		logging.info("configuration: using {}".format(path))
		cdict = utils.readConf(path)
		break
    # -- config specifies the filename of the dict
    elif type(config) == str:
	path=config
	if not os.path.exists(path):
	    die("{}: configuration file goes not exist".format(path))
	logging.info("configuration: using {}".format(path))
	cdict = utils.readConf(path)
    # -- config is the config dict
    elif type(config) == dict:
	logging.info("configuration: using inline config")
	cdict = config

    if cdict == None:
	die("configuration dict is NULL")

    # -- the config dict is supposed to contain "sections"
    if sectionsName == None:
	sectionDict =  cdict
    else:
	sectionDict = cdict[sectionsName]
    if tag not in sectionDict.keys():
	die("{}: tag not found in configuration ({})".format(tag,config))
    sdict = sectionDict[tag]

    # -- optDict will override the config dict
    for key in sdict.keys():
	if not key in optDict:
	    rdict[key] = sdict[key]
	    continue
	if optDict[key] == None or optDict[key] == "" :
	    rdict[key] = sdict[key]

    return rdict

if __name__ == "__main__" :
    odict = {'a': 'a', 'b' : 'b', 'c': '' }
    cdict = {
	'sections' : {
	    'default': {'a': 'a1', 'b' : 'b1', 'c': 'c1','d':'d1' }
	}
    }
    utils.ppr(merge(odict,config=cdict))
