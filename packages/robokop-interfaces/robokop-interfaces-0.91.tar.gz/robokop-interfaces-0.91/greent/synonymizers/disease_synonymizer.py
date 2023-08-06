from greent.util import Text
from greent.synonymizers import oxo_synonymizer

#2/20/2018, OXO doesn't yet understand MONDOs.
# So: if the identifier is a mondo identifier, pull down doids and whatever from mondo xrefs
#     then hit OXO in order of the best identifiers (?)
def synonymize(node,gt):
    curie = Text.get_curie(node.identifier)
    synonyms = set()
    if curie == 'MONDO':
        synonyms.update(synonymize_with_MONDO(node,gt))
        #You might think this is wrong,but it is right.  Even though the synonyms will get added to the node
        #outside, we are also going to add them here so that the OXO synonymizer will find them.
        node.add_synonyms(synonyms)
    synonyms.update(synonymize_with_OXO(node,gt))
    return synonyms

def synonymize_with_MONDO(node,gt):
    print (f" class of mondo: {type(gt.mondo)}")
    syns = set(gt.mondo.mondo_get_doid( node.identifier ))
    syns.update( set(gt.mondo.mondo_get_umls( node.identifier )))
    syns.update( set(gt.mondo.mondo_get_efo( node.identifier )))
    #node.add_synonyms(syns)
    return syns

def synonymize_with_OXO(node,gt):
    return oxo_synonymizer.synonymize(node,gt)


