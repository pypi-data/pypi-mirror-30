from greent.node_types import node_types, DRUG_NAME, DISEASE_NAME, UNSPECIFIED
from greent.util import Text
from greent.program import Program
from greent.program import QueryDefinition

class Transition:
    def __init__(self, last_type, next_type, min_path_length, max_path_length):
        self.in_type = last_type
        self.out_type = next_type
        self.min_path_length = min_path_length
        self.max_path_length = max_path_length
        self.in_node = None
        self.out_node = None

    def generate_reverse(self):
        return Transition(self.out_type, self.in_type, self.min_path_length, self.max_path_length)

    @staticmethod
    def get_fstring(ntype):
        if ntype == DRUG_NAME or ntype == DISEASE_NAME:
            return 'n{0}{{name:"{1}"}}'
        if ntype is None:
            return 'n{0}'
        else:
            return 'n{0}:{1}'

    def generate_concept_cypher_pathstring(self, t_number):
        end   = f'(c{t_number+1}:Concept {{name: "{self.out_type}" }})'
        pstring = ''
        if t_number == 0:
            start = f'(c{t_number}:Concept {{name: "{self.in_type}" }})\n'
            pstring += start
        if self.max_path_length > 1:
            pstring += f'-[:translation*{self.min_path_length}..{self.max_path_length}]-\n'
        else:
            pstring += '--\n'
        pstring += f'{end}\n'
        return pstring

class UserQuery:
    """This is the class that the rest of builder uses to interact with a query."""

    def __init__(self, start_values, start_type, lookup_node):
        """Create an instance of UserQuery. Takes a starting value and the type of that value"""
        self.query = None
        self.definition = QueryDefinition()
        # Value for the original node
        self.definition.start_values = start_values
        self.definition.start_type = start_type
        self.definition.end_values = None
        # The term used to create the initial point
        self.definition.start_lookup_node = lookup_node
        # List of user-level types that we must pass through
        self.add_node(start_type)

    def add_node(self, node_type):
        """Add a node to the node list, validating the type
           20180108: node_type may be None"""
        # Our start node is more specific than this...  Need to have another validation method
        if node_type is not None and node_type not in node_types:
            raise Exception('node type must be one of greent.node_types')
        self.definition.node_types.append(node_type)

    def add_transition(self, next_type, min_path_length=1, max_path_length=1, end_values=None):
        """Add another required node type to the path.

        When a new node is added to the user query, the user is asserting that
        the returned path must go through a node of this type.  The default is
        that the next node should be directly related to the previous. That is,
        no other node types should be between the previous node and the current
        node.   There may be other nodes, but they will represent synonyms of
        the previous or current node.  This is defined using the
        max_path_length input, which defaults to 1.  On the other hand, a user
        may wish to define that some number of other node types must be between
        one node and another.  This can be specified by the min_path_length,
        which also defaults to 1.  If indirect edges are demanded, this
        parameter is set higher.  If this is the final transition, a value for
        the terminal node may be added.  Attempting to add more transitions
        after setting an end value will result in an exception.  If this is the
        terminal node, but it does not have a specified value, then no
        end_value needs to be specified.

        arguments: next_type: type of the output node from the transition.
                              Must be an element of reasoner.node_types.
                   min_path_length: The minimum number of non-synonym transitions
                                    to get from the previous node to the added node
                   max_path_length: The maximum number of non-synonym transitions to get
                                    from the previous node to the added node
                   end_value: Value of this node (if this is the terminal node, otherwise None)
        """
        # validate some inputs
        # TODO: subclass Exception
        if min_path_length > max_path_length:
            raise Exception('Maximum path length cannot be shorter than minimum path length')
        if self.definition.end_values is not None:
            raise Exception('Cannot add more transitions to a path with a terminal node')
        # Add the node to the type list
        self.add_node(next_type)
        # Add the transition
        t = Transition(self.definition.node_types[-2], next_type, min_path_length, max_path_length)
        self.definition.transitions.append(t)
        # Add the end_value
        if end_values is not None:
            self.definition.end_values = end_values

    def add_end_lookup_node(self, lookup_node):
        self.definition.end_lookup_node = lookup_node

    def generate_cypher(self):
        """Generate a cypher query to find paths through the concept-level map."""
        cypherbuffer = ['MATCH p=\n']
        paths_parts = []
        for t_number, transition in enumerate(self.definition.transitions):
            paths_parts.append(transition.generate_concept_cypher_pathstring(t_number))
        cypherbuffer.append( ''.join(paths_parts) )
        last_node_i = len(self.definition.transitions)
        cypherbuffer.append('FOREACH (n in relationships(p) | SET n.marked = TRUE)\n')
        cypherbuffer.append(f'WITH p,c0,c{last_node_i}\n')
        if self.definition.end_values is None:
            cypherbuffer.append(f'MATCH q=(c0:Concept)-[*0..{last_node_i} {{marked:True}}]->(c{last_node_i}:Concept)\n')
        else:
            cypherbuffer.append(f'MATCH q=(c0:Concept)-[*0..{last_node_i} {{marked:True}}]->()<-[*0..{last_node_i} {{marked:True}}]-(c{last_node_i}:Concept)\n')
        cypherbuffer.append('WHERE p=q\n')
        #This is to make sure that we don't get caught up in is_a and other funky relations.:
        cypherbuffer.append('AND ALL( r in relationships(p) WHERE  EXISTS(r.op) )')
        cypherbuffer.append('FOREACH (n in relationships(p) | SET n.marked = FALSE)\n')
        cypherbuffer.append('RETURN p, EXTRACT( r in relationships(p) | startNode(r) ) \n')
        return ''.join(cypherbuffer)

    def compile_query(self, rosetta):
        self.cypher = self.generate_cypher()
        print(self.cypher)
        plans = rosetta.type_graph.get_transitions(self.cypher)
        self.programs = [Program(plan, self.definition, rosetta, i) for i,plan in enumerate(plans)]
        return len(self.programs) > 0

    def get_programs(self):
        return self.programs

    def get_terminal_nodes(self):
        starts = set()
        ends = set()
        return self.query.get_terminal_types()

