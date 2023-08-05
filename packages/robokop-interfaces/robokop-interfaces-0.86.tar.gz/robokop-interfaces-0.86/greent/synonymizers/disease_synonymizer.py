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
    synonyms.update(synonymize_with_OXO(node,gt))
    return synonyms

def synonymize_with_MONDO(node,gt):
    syns = set(gt.mondo.mondo_get_doid( node.identifier ))
    syns.update( set(gt.mondo.mondo_get_umls( node.identifier )))
    syns.update( set(gt.mondo.mondo_get_efo( node.identifier )))
    #node.add_synonyms(syns)
    return syns

def synonymize_with_OXO(node,gt):
    return oxo_synonymizer.synonymize(node,gt)


