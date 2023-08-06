from typing import cast

from faketree.intermake import mutation, tree_generation, output
from faketree.intermake.output import ESubset
from faketree.treedata import NodeData
from intermake import command
from intermake.engine.environment import MCMD
from mgraph import MGraph
from mhelper import array_helper, bio_helper, ansi
from mhelper.io_helper import MemoryWriter


@command()
def test_groot():
    """
    Tests the groot test creation procedure.
    """
    
    # The following is the GROOT test protocol
    args_random_tree = { "suffix": "1", "delimiter": "_", "size": 10, "outgroup": True }
    args_seqgen = "-d 0.2"
    
    outgroups = tree_generation.random_tree( ["A", "B", "C"], **args_random_tree )
    a, b, c = (x.parent for x in outgroups)
    
    mutation.seqgen( [a, b, c], args_seqgen )
    
    fa = tree_generation.random_node( a, avoid = outgroups )
    fb = tree_generation.random_node( b, avoid = outgroups )
    tree_generation.branch( [fa, fb], c )
    mutation.mk_composite( [c] )
    
    output.show()
    
    mutation.apply()
    
    c_start, c_end = __gb()
    
    fasta = __get_leaf_fasta()
    true_fasta = []
    
    for accession, sequence in bio_helper.parse_fasta( text = fasta ):
        if accession.startswith( "B" ):
            true_fasta.append( ">" + accession )
            true_fasta.append( sequence )
        elif accession.startswith( "C" ):
            true_fasta.append( ">" + accession )
            true_fasta.append( sequence[c_start - 1:c_end] )
    
    graph = __make_nj_tree( "\n".join( true_fasta ), outgroups[1].data )
    
    MCMD.print( graph.to_ascii( fnode = __fn ))
    
    
def __fn( x ):
    if not x.has_children:
        if x.data.startswith( "B" ):
            c = ansi.FORE_RED
        elif x.data.startswith( "C" ):
            c = ansi.FORE_YELLOW
        
        return c + x.data + ansi.RESET
    else:
        return "--"


def __gb():
    # We're interested in pulling out the "B" sequences
    blasts = output.get_blasts()
    
    for blast in blasts:
        if (cast( NodeData, blast.query_node.data ).name.startswith( "B" )
                and cast( NodeData, blast.subject_node.data ).name.startswith( "C" )):
            return blast.subject_start, blast.subject_end
        
        if (cast( NodeData, blast.query_node.data ).name.startswith( "C" )
                and cast( NodeData, blast.subject_node.data ).name.startswith( "B" )):
            return blast.query_start, blast.query_end
    
    raise ValueError( "Not found." )


@command()
def test_seqgen():
    """
    Tests seq-gen.
    """
    
    args_random_tree = { "suffix": "1", "delimiter": "_", "size": 10, "outgroup": True }
    args_seqgen = "-d 0.2"
    outgroup_a, outgroup_b = tree_generation.random_tree( ["A", "B"], **args_random_tree )
    outgroup_a_data: NodeData = outgroup_a.data
    root_a = outgroup_a.parent
    root_b = outgroup_b.parent
    
    mutation.seqgen( [root_a], args_seqgen )
    mutation.seqgen( [root_b], args_seqgen )
    
    join_point_a = tree_generation.random_node( root_a, avoid = [outgroup_a] )
    tree_generation.branch( [join_point_a], root_b )
    tree_generation.remove( [root_b] )
    
    output.show()
    mutation.apply()
    fasta = __get_leaf_fasta()
    graph = __make_nj_tree( fasta, outgroup_a_data )
    
    MCMD.print( "OUTGROUP IS {}".format( outgroup_a ) )
    MCMD.print( "INPUT" )
    output.show( mutator = False, length = False, clades = False )
    MCMD.print( "RESULT" )
    MCMD.print( graph.to_ascii( fnode = lambda x: str( x ) if not x.has_children else "--" ) )


def __get_leaf_fasta():
    output.fasta( which = ESubset.LEAVES, file = "memory" )
    fasta = MemoryWriter.retrieve()
    return fasta


def __make_nj_tree( fasta, outgroup_a_data ):
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import groot
    # noinspection PyPackageRequirements
    from groot.algorithms.extendable import tree as groot_tree
    newick = groot_tree.tree_neighbor_joining( "p", fasta )
    from mgraph import importing
    graph = importing.import_newick( newick )
    graph.nodes[outgroup_a_data.name].parent.make_root()
    return graph
