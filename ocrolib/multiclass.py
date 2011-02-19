#!/usr/bin/python

# DEPRECATED -- use gatedclass.py instead

import random as pyrandom
import code,pickle,sys,os,re,traceback,cPickle,os.path,glob
from optparse import OptionParser
from pylab import *
from scipy import stats
import common as ocrolib
from common import deprecated
import dbtables,quant,utils

def average_outputs(os):
    result = {}
    for o in os:
        for k,v in o:
            result[k] = result.get(k,0.0)+v
    n = 1.0*len(os)
    return [(k,v/n) for k,v in result.items()]

class MultiClass:
    @deprecated
    def __init__(self):
        self.center_extractor = ocrolib.BboxFE()
        self.vectors = []
        self.cutoffs = []
        self.models = []
    def add(self,center,cutoff,model):
        self.vectors.append(center)
        self.cutoffs.append(cutoff)
        self.models.append(model)
    def extract(self,image):
        v = self.center_extractor.extract(image)
        v /= sqrt(sum(v**2))
        return v
    def coutputs(self,image,geometry=None):
        outputs = []
        v = self.extract(image)
        def maybe_dist(v,c):
            if c is None: return 0.0
            return quant.dist(v.ravel(),c.ravel())
        dists = array([maybe_dist(v,c) for c in self.vectors],'f')
        for i in range(len(dists)):
            if self.cutoffs[i] is None or dists[i]<self.cutoffs[i]:
                output = self.models[i].coutputs(image,geometry=geometry)
                outputs.append(output)
        return average_outputs(outputs)
    def coutputs_batch(self,vs,geometries=None):
        outputs = []
        for i in range(len(vs)):
            v = vs[i]
            geometry = None
            if geometries is not None: geometry = geometries[i]
            outputs.append(self.coutputs(v,geometry=geometry))
        return outputs
    def setExtractor(self,extractor):
        ocrolib.warn_once("setExtractor called")

def load_multiclass(mc,dir):
    paths = glob.glob(dir+"/*.cmodel") + glob.glob(dir+"/*.model") 
    print "# loading",len(paths),"models"
    for path in paths:
        model = ocrolib.load_component(path)
        base,_ = os.path.splitext(path)
        if os.path.exists(base+".info"):
            with open(base+".info","r") as stream:
                info = cPickle.load(stream)
            center = info.center
            cutoff = info.cutoffs[int(len(info.cutoffs)*mc.cutoff)]
        else:
            center = None
            cutoff = 1e38
        print "#",path,cutoff
        mc.addClassifier(center,cutoff,model)
