import re
import sys
import os
from ConnyUtils import IOUtil
from ConnyUtils import Common
import numpy as np

# helper to calculate similarity
def getSimilarity(a,b,model,logging=True):
    s = 0.0
    try:
        s = model.similarity(a, b)
    except KeyError as err:
        print("Error", err, a,"<-->", b)
        pass
    if(logging):
        print(a, "<-->", b, " = ", s)
    return s,a,b

# FastTextModel expected
def evalModelSysonym(fastTextModel):
    # Load relations
    import pkg_resources
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join(('packageData', 'skill_relations.txt'))  # Do not use os.path.join(), see below

    raw_relations = pkg_resources.resource_string(resource_package, resource_path).splitlines()
    # or for a file-like stream:
    _relations = Common.LamdaList(raw_relations)\
        .map(lambda s : s.decode('utf-8'))\
        .map(
        lambda s: s.split(" ")).result()
    # reshape array to dict with key as target_relation and value as source_relations array.
    relations = dict([(x[0], x[1:]) for x in _relations])

    results = []
    # iterate to get relating pairs
    for target_relation, source_relations in relations.items():
        for source_relation in source_relations:
            s, a, b = getSimilarity(target_relation, source_relation, fastTextModel, logging=True)
            results.append(s)
    return {"mean_result": np.mean(results), "results": results}