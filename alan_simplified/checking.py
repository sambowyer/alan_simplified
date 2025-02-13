from typing import Optional, Any

from .Plate import Plate, tree_branches, tree_values
from .Group import Group
from .dist import Dist

#### Check the structure of the distributions match.

def check_support(name:str, distP:Dist, distQ:Any):
    supportQ = distQ.dist.support 
    supportP = distP.dist.support 
    if supportQ != supportP:
        raise Exception(f"Distributions in P and Q for {nameP} have different support.  For P: {supportP}.  While for Q: {supportQ}")

def check_PQ_group(groupname: str, groupP: Group, groupQ: Group):
    mismatch_names(f"In group {groupname}, there is a mismatch in the keys, with", groupP.prog.keys(), groupQ.prog.keys())
    for varname, distP in groupP.prog.items():
        distQ = groupQ.prog[varname]
        check_support(varname, distP, distQ)

def mismatch_names(prefix:str, namesP: list[str], namesQdata: list[str]):
    #Check for mismatches between two lists of names (usually P and Q+data).
    inPnotQ = list(set(namesP).difference(namesQdata))
    inQnotP = list(set(namesQdata).difference(namesP))
    if 0 < len(inPnotQ):
        raise Exception(f"{prefix} {inPnotQ} present in P but not Q + data")
    if 0 < len(inQnotP):
        raise Exception(f"{prefix} {inQnotP} present in Q + data, but not in P")



def check_PQ_plate(platename: Optional[str], P: Plate, Q: Plate, data: dict):
    """
    Checks that 
    * P and Q have the same Plate/Group structure
    * Distributions in P and Q have the same support
    Doesn't check:
    * Uniqueness of names
    """

    #Check for mismatches between P and Q+data.
    namesP = P.prog.keys()
    namesQdata = [*Q.prog.keys(), *tree_values(data).keys()]
    mismatch_names(f"In plate {platename}, there is a mismatch in the keys, with", namesP, namesQdata)
    #Now, any name in Q or data must appear in P.

    #Go through the names in data and the names in Q separately.

    #First, names in data.
    #data must correspond to a Dist in P.
    for name in tree_values(data).keys():
        distP = P.prog[name]
        if not isinstance(distP, Dist):
            raise Exception(f"{name} in appears in Plate {platename} as data, so the corresponding {name} in P should be a distribution over a single random variable.  But actually {name} in P is something else: {type(distP)}")

    #Now check names in Q 
    for name, dgpt_Q in P.prog.items():
        if isinstance(dgpt_Q, Dist):
            distQ = dgpt_Q
            distP = P.prog[name]
            if not isinstance(distP, Dist):
                raise Exception(f"{name} in Q is a Dist, so it should also be a Group in P, but actually its a {type(distP)}.")
            check_support(name, distP, distQ)
        elif isinstance(dgpt_Q, Group):
            groupQ = dgpt_Q
            groupP = P.prog[name]
            if not isinstance(groupP, Group):
                raise Exception(f"{name} in Q is a Group, so it should also be a Group in P, but actually its a {type(groupP)}.")
            check_PQ_group(name, groupP, groupQ)
        else:
            assert isinstance(dgpt_Q, Plate)
            plateQ = dgpt_Q
            plateP = P.prog[name]
            if not isinstance(plateP, Plate):
                raise Exception(f"{name} in Q is a Plate, so it should also be a Plate in P, but actually its a {type(plateP)}.")
            check_PQ_plate(name, plateP, plateQ, data[name])
