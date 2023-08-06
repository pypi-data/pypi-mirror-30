import pytest
from greent.graph_components import KNode
from greent.ontologies.mondo2 import Mondo2
from greent.servicecontext import ServiceContext
from greent import node_types

@pytest.fixture(scope='module')
def mondo2():
    return Mondo2(ServiceContext.create_context())

def test_huntington_is_genetic(mondo2):
    huntington = KNode('OMIM:143100',node_types.DISEASE)
    assert mondo2.is_genetic_disease(huntington)

def test_lookup(mondo2):
    terms1=mondo2.search('Huntington Disease')
    terms2=mondo2.search("Huntington's Chorea")
    assert len(terms1) == len(terms2) == 1
    assert terms1[0] == terms2[0] == 'MONDO:0007739'

