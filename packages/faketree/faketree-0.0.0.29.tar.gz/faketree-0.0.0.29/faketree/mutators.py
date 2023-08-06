import random
from typing import Set, List, cast, Optional

from os import path

from faketree.treedata import FtBlast, FtSequence, FtSite, FtSiteName, NodeData
from intermake import MENV, constants
from mgraph import MNode, FollowParams, exporting
from mgraph.graphing import EDirection
from mhelper import string_helper, LogicError, safe_cast, bio_helper, Logger, abstract, virtual
from intermake import subprocess_helper


class Frame:
    def __init__( self, sequence: FtSequence, blast: List[FtBlast], _no_check: bool = False ):
        if not _no_check:
            assert isinstance( sequence, FtSequence )
            assert isinstance( blast, list )
            assert not blast or all( isinstance( x, FtBlast ) for x in blast )
        
        self.sequence = sequence
        self.blast = blast
    
    
    WAITING = None
    WORKING = None


Frame.WAITING = Frame( cast( FtSequence, None ), cast( list, None ), True )
Frame.WORKING = Frame( cast( FtSequence, None ), cast( list, None ), True )

LOG = Logger( "mutators", True )
LOG_SG = Logger( "seqgen", True )


@abstract
class Mutation:
    """
    ABSTRACT.
    
    Base class for mutations.
    Concrete instances of these classes are assigned to nodes (`NodeData`) to manage their evolution.
    """
    
    
    def __init__( self, node: MNode ):
        """
        CONSTRUCTOR
        The derived class may perform additional setup.
        :param node: Node to manage 
        """
        self.__node = node
    
    
    @property
    def node( self ) -> MNode:
        return self.__node
    
    
    def reset( self ):
        """
        Called before evolution is simulated in order to resets
        the node data and any dynamic state of the mutation. 
        """
        self.node.data.sequence = None
        self.node.data.blast = None
        self.on_reset()
    
    
    def mutate( self ) -> bool:
        """
        Mutates the node.
        
        :return:    A value `True` to indicate a change in status, or `False` to indicate no change in status. 
        """
        d = self.node.data
        assert isinstance( d, NodeData )
        if d.sequence is None:
            r: Frame = self.on_mutate()
            
            if r is None:
                raise ValueError( ":method:`on_mutate` must return a value." )
            if r is Frame.WAITING:
                return False
            elif r is Frame.WORKING:
                return True
            
            assert r.sequence is not None
            assert r.blast is not None
            
            d.sequence = r.sequence
            d.blast = r.blast
            
            return True
        else:
            assert d.blast is None
            return False
    
    
    @virtual
    def on_reset( self ) -> None:
        """
        The derived class may override to initialise or reset any dynamic state the instance may
        possess. This is called prior to evoltion and calls to `on_mutate`.
        :return: 
        """
        pass
    
    
    @abstract
    def on_mutate( self ) -> Frame:
        """
        The derived class must override to perform the evolution.
        
        :return: A `Frame` must be returned, detailing the evolution.
                    Frame(...)    - signals that the node has evolved, the passed arguments are applied to the node.
                                    `on_mutate` will not be called again for this simulation run
                    Frame.WAITING - signals that this node is waiting for other nodes to complete their evolution
                                    `on_mutate` will be called again after other nodes are processed
                                    if all nodes return WAITING the evolution is considered deadlocked and an error is raised  
                    Frame.WORKING - signals that this node has performed work but requires another call to be made
                                    `on_mutate` will be called again after other nodes are processed  
                  
        """
        raise NotImplementedError( "abstract" )


class MutationWithPool( Mutation ):
    DEFAULT_POOL = "ACEFGHIKLMNPQRSTVWY"
    
    
    def __init__( self, node: MNode, pool: str ):
        super().__init__( node )
        self.__pool = pool
    
    
    @property
    def use_pool( self ) -> str:
        if self.__pool:
            return self.__pool
        else:
            return MutationWithPool.DEFAULT_POOL
    
    
    def format_display_pool( self, text ):
        if self.__pool:
            return text.replace( "*", self.__pool )
        else:
            return ""
    
    
    def pick_from_pool( self, disregard = None ):
        if disregard:
            choices = list( self.use_pool )
            
            for old_site in disregard:
                if old_site in choices:
                    choices.remove( old_site )
                else:
                    raise ValueError( "«{}» not in «{}»".format( old_site, choices ) )
        else:
            choices = self.use_pool
        
        if not choices:
            raise ValueError( "Cannot pick from pool because the pool is empty (this may be after disregarding certain sites). Change your mutation parameters and try again." )
        
        r = random.choice( choices )
        
        if disregard and r in disregard:
            raise ValueError( "Sorry. I chose «{}» from «{}» but you told me not to do that.".format( r, self.use_pool ) )
        
        return r
    
    
    def on_mutate( self ) -> Frame:
        raise NotImplementedError( "abstract" )


class UniqueMutationRoot( MutationWithPool ):
    def __init__( self, node: MNode, pool: str, amplitude: int ):
        super().__init__( node, pool )
        self.dyn_sequence_out = FtSequence( "" )
        self.amplitude = amplitude
    
    
    def on_reset( self ):
        self.dyn_sequence_out = FtSequence( "" )
    
    
    def acquire_unique_index( self ) -> FtSiteName:
        name = FtSiteName()
        self.dyn_sequence_out.add_site( FtSite( name = name, site = self.pick_from_pool() ) )
        return name
    
    
    def on_mutate( self ) -> Frame:
        # Find all descendants
        de = self.node.list_descendants()
        for descendant in de:
            if isinstance( descendant.data.mutator, UniqueMutation ):
                if descendant.data.mutator.dyn_site_names is None:
                    # Not all descendants are yet ready
                    return Frame.WAITING
        
        # Root has no BLAST
        blast = []
        
        # We must shuffle the result, or, when `amplitude` is > 1 adjacent sites will always mutate together, which causes problems for alignments
        random.shuffle( self.dyn_sequence_out.data )
        
        LOG( "{}: 🔧 Unique.root; length = {}", self.node, len( self.dyn_sequence_out ) )
        
        return Frame( self.dyn_sequence_out, blast )
    
    
    def __str__( self ):
        if self.amplitude == 1:
            a = ""
        else:
            a = "+{} ".format( self.amplitude )
        
        return "🔧 UNIQUE MUTATION {}ROOT{}".format( a, self.format_display_pool( " (pool=*)" ) )


class RandomMutationRoot( MutationWithPool ):
    
    
    def __init__( self, node: MNode, length: int, pool: str ):
        super().__init__( node, pool )
        self.intended_length = length
    
    
    def __str__( self ):
        return "💥 RANDOM SEQUENCE ({}{})".format( self.format_display_pool( "*=" ), self.intended_length )
    
    
    def on_mutate( self ) -> Frame:
        r = []
        
        for _ in range( self.intended_length ):
            r.append( self.pick_from_pool() )
        
        sequence_result = FtSequence( "".join( r ) )
        blast_result = []  # root has no blast
        
        LOG( "{}: 💥 Random.root; length = {}", self.node, len( sequence_result ) )
        
        return Frame( sequence_result, blast_result )


class RandomMutation( MutationWithPool ):
    def __init__( self, node: MNode, chance: float, pool: str ):
        super().__init__( node, pool )
        self.intended_chance = chance
    
    
    def on_mutate( self ) -> Frame:
        sequence = FtSequence()
        
        if self.node.num_parents != 1:
            raise ValueError( "Cannot apply a random mutation to a node with «{}» parents.".format( self.node.num_parents ) )
        
        if self.node.parent.data.sequence is None:
            return Frame.WAITING
        
        num_changes = 0
        
        for site in self.node.parent.data.sequence:
            assert isinstance( site, FtSite )
            
            if random.random() >= self.intended_chance:
                sequence.add_site( site )
            else:
                num_changes += 1
                sequence.add_site( FtSite( name = site.name, site = self.pick_from_pool() ) )
        
        blasts = [FtBlast( self.node, self.node.parent, 1, len( sequence ), 1, len( sequence ) )]
        
        LOG( "{}: ▶️ Random.child; inherits = {}, changed = {} of {}", self.node, self.node.parent, num_changes, len( sequence ) )
        
        return Frame( sequence, blasts )
    
    
    def __str__( self ):
        return "▶️ RANDOM MUTATIONS ({}{})".format( self.format_display_pool( "*=" ), self.intended_chance )


class FixedSequence( Mutation ):
    def __init__( self, node: MNode, sequence: str ):
        super().__init__( node )
        self.intended_sequence = sequence
    
    
    def on_mutate( self ) -> Frame:
        sequence = FtSequence( self.intended_sequence )
        blasts = []
        
        LOG( "{}: 📝 Fixed; length = {}", self.node, len( sequence ) )
        
        return Frame( sequence, blasts )
    
    
    def __str__( self ):
        return "📝 " + self.intended_sequence


class CombinationMutation( Mutation ):
    def on_mutate( self ) -> Frame:
        r = FtSequence()
        b = []
        
        for parent in sorted( self.node.parents, key = lambda x: x.data.name ):
            s = parent.data.sequence
            if s is None:
                return Frame.WAITING
            
            start, end = r.extend( s )
            b.append( FtBlast( self.node, parent, start + 1, end, 1, len( s ) ) )
        
        LOG( "{}: ‼️ Composite; inherits = {}, lengths = {}, final = {}", self.node, self.node.parents, [len( x.data.sequence ) for x in self.node.parents], len( r ) )
        
        return Frame( r, b )
    
    
    def __str__( self ):
        return "‼️ COMPOSITE {}".format( string_helper.format_array( self.node.parents, final = " and " ) )


class SeqgenMutation( Mutation ):
    """
    Uses SeqGen to perform the mutation.
    
    This behaves a little differently than the other mutators - there is no _root_ managing a set of _descendants_ 
    - this is because the root may itself be sourced from a different mutator.
    
    i.e.
    ```
                                  |-- . . .
                    |---(SEQGEN)--|
                    |             |-- . . .
    . . . (RANDOM)--|                            <- this is the root but it's not a seqgen
                    |             |-- . . .
                    |---(SEQGEN)--|
                                  |-- . . .
    ```
    
    
    """
    
    
    def __init__( self, node: MNode, length: int, seq_len: int, parameters: str, uid: object ):
        super().__init__( node )
        self.edge_length = length
        self.seq_len = seq_len
        self.parameters = parameters
        self.uid = uid
        
        self.dyn_reg_sequence = None
    
    
    def __str__( self ):
        return "🖥 SEQGEN"
    
    
    def is_compatible( self, node: MNode ):
        if node is None:
            return False
        
        d = safe_cast( NodeData, node.data )
        
        if not isinstance( d.mutator, SeqgenMutation ):
            return False
        
        if d.mutator.parameters != self.parameters:
            return False
        
        if d.mutator.uid != self.uid:
            return False
        
        return True
    
    
    def on_reset( self ):
        self.dyn_reg_sequence = None
    
    
    def on_mutate( self ) -> Frame:
        # Sanity checks
        if self.node.num_parents > 1:
            raise ValueError( "{}: SeqGenMutation node should have 0 or 1 parents but this has {}.".format( self.node, self.node.num_parents ) )
        
        # In all cases I need my parent(s) to complete
        if self.node.has_parents and not self.node.parent.data.sequence:
            return Frame.WAITING
        
        # The first node called is responsible for the work
        # (yes, there can be two "roots" provided they are siblings) 
        if self.dyn_reg_sequence:
            if self.node.has_parents:
                return self.__use_registered_sequence( self.node.parent.data.sequence )
            else:
                return self.__use_new_sequence()
        
        # Let's do this
        assert not self.node.has_parents or not self.is_compatible( self.node.parent ), "{}: Parent should be doing the work, not me.".format( self.node )
        
        # Get the "true root"
        if self.node.has_parents:
            true_root = self.node.parent
            origin = true_root.data.sequence
            arg_1k = "-k"
            arg_1v = "1"
            LOG_SG( "{}: The MRCA exists - {}", self.node, true_root )
        else:
            true_root = self.node
            origin = None
            arg_1k = "-l"
            arg_1v = str( self.seq_len )
            LOG_SG( "{}: The MRCA is not built", self.node )
        
        graph = true_root.graph
        subset = graph.follow( FollowParams( start = true_root, node_filter = self.is_compatible, direction = EDirection.OUTGOING ) ).visited_nodes
        subtree = graph.copy( nodes = subset )
        subtree_newick = exporting.export_newick( subtree,
                                                  fnode = lambda x: x.data.name,
                                                  fedge = lambda x: str( x.right.data.mutator.edge_length ),
                                                  internal = False )
        
        assert subtree.find_node( true_root ).is_root, "Expected true_root to still be the root after sub-graphing."
        LOG_SG( "{}: Taking the subset {}", self.node, subset )
        LOG_SG( "{}", subtree.to_ascii() )
        LOG_SG( "{}: {}", self.node, subtree_newick )
        
        # Prepare the input
        file_name = path.join( MENV.local_data.local_folder( constants.FOLDER_TEMPORARY ), "seq_gen.newick" )
        
        with open( file_name, "w" ) as file_out:
            if origin:
                file_out.write( "1 {}\n".format( len( origin ) ) )
                file_out.write( "root    {}\n".format( origin ) )
                file_out.write( "1" )
            
            file_out.write( subtree_newick + "\n" )
        
        # Run seqgen
        stdout = []
        args = ["seq-gen",
                "-m", "MTREV",
                arg_1k, arg_1v,
                "-wa"]
        args.extend( x for x in self.parameters.split( " " ) if x )
        args.append( file_name )
        LOG_SG( "{}: Running {}", self.node, args )
        subprocess_helper.run_subprocess( args,
                                          collect_stdout = stdout.append,
                                          hide = True )
        
        # Parse the output
        nodes = dict( (x.data.name, x) for x in subtree )
        pending = []
        
        # Add the results!
        # - Note that Seqgen outputs bad Fasta and an incorrect sequence count for Phylip,
        #   so we need to process the output manually so we can fiddle with it
        for accession, sequence in bio_helper.parse_phylip( lines = stdout, ignore_num_seq = True ):
            node = nodes.get( accession )
            LOG_SG( "{}: ***** ACCESSION: {}", self.node, accession )
            
            if node is not None:
                LOG_SG( "{}:        - ASSIGN: {}", self.node, accession )
                self.set_reg_sequence_on( node, sequence, true_root, origin )
                
                while pending:
                    node = node.parent
                    LOG_SG( "{}:   - POP PENDING: {}", self.node, node )
                    self.set_reg_sequence_on( node, pending.pop(), true_root, origin )
            else:
                assert accession.isdigit(), "Can't find the accession «{}» and it's not a number.".format( accession )
                
                LOG_SG( "{}:  - PUSH PENDING: {}", self.node, accession )
                pending.append( sequence )
        
        # Some sanity checks
        unassigned = []
        
        for node in subtree:
            if isinstance( node.data.mutator, SeqgenMutation ):
                if node.data.mutator.dyn_reg_sequence is None:
                    unassigned.append(node)
        
        if unassigned:
            raise ValueError( "{}: Failed to provide a sequence to all nodes: «{}» are unassigned. Check the log for details.".format( self.node, unassigned ) )
        
        if pending:
            raise ValueError( "‘SeqGenMutation’ on the node «{}». Expected SeqGen output to be ordered and have the same number of sequences as in the initial tree, but «{}» sequences are in the output that haven't been assigned. Something went wrong. Try turning on «{}» logging and rerun your query.".format( self.node, len( pending ), LOG_SG.name ) )
        
        # We've all done, return asking to be called back one last time
        return Frame.WORKING
    
    
    def __use_new_sequence( self ) -> Frame:
        result = FtSequence()
        
        for new_site in self.dyn_reg_sequence:
            result.add_site( FtSite( name = FtSiteName(), site = new_site ) )
        
        self.all_done = True
        return Frame( result, [] )
    
    
    def __use_registered_sequence( self, ancestor_sequence: FtSequence ) -> Frame:
        result = FtSequence()
        
        assert isinstance( ancestor_sequence, FtSequence ), ancestor_sequence
        assert isinstance( self.dyn_reg_sequence, str )
        
        if len( ancestor_sequence ) != len( self.dyn_reg_sequence ):
            raise ValueError( "{}: Mutated sequence not same length «{}» as its origin «{}».".format( self.node, len( self.dyn_reg_sequence ), len( ancestor_sequence ) ) )
        
        for old_site, new_site in zip( ancestor_sequence, self.dyn_reg_sequence ):
            assert isinstance( old_site, FtSite )
            assert isinstance( new_site, str )
            result.add_site( FtSite( name = old_site.name, site = new_site ) )
        
        blast = FtBlast( self.node, self.node.parent, 1, len( result ), 1, len( result ) )
        self.all_done = True
        return Frame( result, [blast] )
    
    
    def set_reg_sequence_on( self, node: MNode, sequence: str, true_root: MNode, origin: Optional[FtSequence] ):
        if node.uid == true_root.uid and origin:
            LOG_SG( "{}: Node is the root {}", self.node, node )
            if sequence != str( origin ):
                raise ValueError( "The origin sequence changed. I don't understand that." )
            return
        
        assert isinstance( node.data.mutator, SeqgenMutation ), "Didn't expect to assign to a non-SeqgenMutation."
        
        if node.data.mutator.dyn_reg_sequence:
            raise ValueError( "Cannot set a reg_sequence on this node {} «{}» because it already has one. The root is {} {} and the origin is {}.".format( id( node ), node, id( true_root ), true_root, bool( origin ) ) )
        
        node.data.mutator.dyn_reg_sequence = sequence


class UniqueMutation( MutationWithPool ):
    def __init__( self, node: MNode, pool: str, amplitude: int ):
        super().__init__( node, pool )
        self.dyn_site_names: Set[FtSiteName] = None
        self.amplitude = amplitude
    
    
    def on_reset( self ):
        self.dyn_site_names = None
    
    
    def on_mutate( self ) -> Frame:
        if self.node.num_parents != 1:
            raise ValueError( "This node «{}» has a `UniqueMutation` but it has no parent. Set this node as a child of another, or change its mutation type to `UniqueMutationRoot`.".format( self.node ) )
        
        # Get the parent sequence
        parent_sequence = self.node.parent.data.sequence
        
        if self.dyn_site_names is None:
            ancestors = self.__get_viable_ancestors()
            
            if not ancestors:
                raise ValueError( "UniqueMutation isn't viable because the node has no UniqueMutationRoot ancestors." )
            
            lst = set()
            
            for ancestor in ancestors:
                for i in range( self.amplitude ):
                    for j in range( ancestor.amplitude ):
                        lst.add( ancestor.acquire_unique_index() )
            
            self.dyn_site_names = lst
            
            if parent_sequence is None:
                return Frame.WORKING
        
        elif parent_sequence is None:
            return Frame.WAITING
        
        r = FtSequence()
        
        for s in parent_sequence:
            if s.name in self.dyn_site_names:
                old_site = s.site
                
                new_site = self.pick_from_pool( disregard = old_site )
                
                if new_site == old_site:
                    raise LogicError( "This mutation is not a mutation but a UniqueMutation must be guaranteed. («{}»): «{}» --> «{}»".format( self, old_site, new_site ) )
                
                r.add_site( FtSite( site = new_site, name = s.name ) )
            else:
                r.add_site( FtSite( site = s.site, name = s.name ) )
        
        assert len( r ) == len( parent_sequence )
        
        b = [FtBlast( self.node, self.node.parent, 1, len( r ), 1, len( r ) )]
        
        return Frame( r, b )
    
    
    def __get_viable_ancestors( self ):
        ancestors = []
        visits = [self.node]
        for visit in visits:
            if isinstance( visit.data.mutator, UniqueMutationRoot ):
                ancestors.append( visit.data.mutator )
                continue
            
            for parent in visit.parents:
                visits.append( parent )
        return ancestors
    
    
    def __str__( self ):
        if self.amplitude == 1:
            a = ""
        else:
            a = "+{} ".format( self.amplitude )
        return "↖️ UNIQUE MUTATION {}FROM {}{}".format( a, string_helper.format_array( (x.node for x in self.__get_viable_ancestors()), final = " or " ), self.format_display_pool( " (pool=*)" ) )
