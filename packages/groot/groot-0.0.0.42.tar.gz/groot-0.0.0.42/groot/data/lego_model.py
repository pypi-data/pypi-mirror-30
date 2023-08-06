"""
Holds the Lego model :class:`LegoModel` and associated objects.
"""

import re
import warnings
from typing import Dict, FrozenSet, Iterable, Iterator, List, Optional, Sequence, Set, Tuple, Any, cast
from intermake import EColour, IVisualisable, UiInfo, MENV
from intermake_qt import resources as intermake_resources
from mgraph import MGraph, Split
from mhelper import MEnum, NotFoundError, SwitchError, TTristate, array_helper, bio_helper, file_helper as FileHelper, string_helper, exception_helper

from groot import constants
from groot.data.exceptions import NotReadyError, InUseError
from groot.constants import LegoStage
from groot.frontends.gui.gui_view_support import EMode
from groot.frontends.gui.forms.resources import resources as groot_resources


TEXT_EDGE_FORMAT = "{}[{}:{}]--{}[{}:{}]"
TEXT_SEQ_FORMAT = "{}"

__author__ = "Martin Rusilowicz"


class EPosition( MEnum ):
    """
    Node positions.
    
    :data NONE:     No specific position
    :data ROOT:     Node is a root. Many software and algorithms only allow named taxa on leaves so this isn't recommended.
    :data OUTGROUP: Node is an outgroup.
    """
    NONE = 0
    ROOT = 1
    OUTGROUP = 2


class ILegoNode:
    """
    Things that can be data on graph nodes.
    i.e. Genes/Taxa (`LegoSequence`) and fusions (`FusionPoint`).
    """
    pass


class ILegoSelectable:
    """
    Components of the model the user can select.
    """
    pass


class FastaError( Exception ):
    """
    Returned by `IHasFasta.to_fasta` when the request cannot be completed.
    """
    pass


# noinspection PyAbstractClass
class IHasFasta( IVisualisable ):
    def to_fasta( self ) -> str:
        """
        The derived class should return FASTA data commensurate with the request.
        :except FastaError: Request cannot be completed.
        """
        raise NotImplementedError( "abstract" )


class ESiteType( MEnum ):
    """
    Type of sites.
    
    :data UNKNOWN:  Unknown site type. Placeholder only until the correct value is identified. Not usually a valid option. 
    :data PROTEIN:  For peptide sequences "IVLFCMAGTSWYPHEQDNKR"
    :data DNA:      For DNA nucleotide sequences "ATCG"
    :data RNA:      For RNA nucleotide sequences "AUCG". For completeness only. Custom/extension algorithms are not expected to support this. Please convert to DNA first!
    """
    UNKNOWN = 0
    PROTEIN = 1
    DNA = 2
    RNA = 3


class ETristate( MEnum ):
    """
    General tristate. More specific to the user than `True`, `False`, `None`.
    
    :data UNKNOWN: Not specified or unknown
    :data YES:     The affirmative
    :data NO:      Opposite of yes
    """
    UNKNOWN = 0
    YES = 1
    NO = -1


class LegoEdge( ILegoSelectable, IHasFasta ):
    """
    Edge from one subsequence (or set of subsequences) to another
    
    These undirected edges have a "left" and "right" list:
        * All subsequences in a list (left or right) must reference the same sequence
        * The left and right sequences cannot reference the same sequence
            * This also implies any element in left cannot be in right and vice-versa
    """
    
    
    def __init__( self, source: "LegoSubsequence", destination: "LegoSubsequence" ) -> None:
        """
        CONSTRUCTOR
        """
        self.left: LegoSubsequence = source
        self.right: LegoSubsequence = destination
        self.is_destroyed = False
        self.comments = []  # type: List[str]
    
    
    def to_fasta( self ) -> str:
        fasta = []
        fasta.append( ">{} [ {} : {} ]".format( self.left.sequence.accession, self.left.start, self.left.end ) )
        fasta.append( self.left.site_array or ";MISSING" )
        fasta.append( "" )
        fasta.append( ">{} [ {} : {} ]".format( self.right.sequence.accession, self.right.start, self.right.end ) )
        fasta.append( self.right.site_array or ";MISSING" )
        fasta.append( "" )
        return "\n".join( fasta )
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE
        """
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Edge",
                       value = "",
                       colour = EColour.CYAN,
                       icon = intermake_resources.folder,
                       extra_named = (self.left, self.right) )
    
    
    def __contains__( self, item: "LegoSequence" ) -> bool:
        """
        OVERRIDE
        Does the edge specify a sequence as either of its endpoints? 
        """
        return item in self.left or item in self.right
    
    
    @staticmethod
    def to_string( sequence: "LegoSequence", start: int, end: int, sequence_b: "LegoSequence", start_b: int, end_b: int ) -> str:
        return LegoSubsequence.to_string( sequence, start, end ) + "--" + LegoSubsequence.to_string( sequence_b, start_b, end_b )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        if self.is_destroyed:
            return "DELETED_EDGE"
        
        return self.to_string( self.left.sequence, self.left.start, self.left.end, self.right.sequence, self.right.start, self.right.end )
    
    
    TSide = "Union[LegoSequence,LegoSubsequence,LegoComponent,bool]"
    
    
    def position( self, item: TSide ) -> bool:
        """
        Returns `True` if `item` appears in the `destination` list, or `False` if it appears in the `source` list.
        
        Supports: Sequence, subsequence or component. Note that only the component of the SEQUENCE is considered, not the individual subsequences.
        
        Raises `KeyError` if it does not appear in either.
        """
        if isinstance( item, LegoSubsequence ):
            if item.sequence is self.left.sequence:
                return False
            
            if item.sequence is self.right.sequence:
                return True
            
            raise KeyError( "I cannot find the subsequence '{}' within this edge.".format( item ) )
        elif isinstance( item, LegoSequence ):
            if item is self.left.sequence:
                return False
            
            if item is self.right.sequence:
                return True
            
            raise KeyError( "I cannot find the sequence '{}' within this edge. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
        elif isinstance( item, LegoComponent ):
            if self.left.sequence in item.major_sequences:
                if self.right.sequence in item.major_sequences:
                    raise KeyError( "I can find the component '{}' within this edge, but both sides of the edge have this same component. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
                
                return False
            
            if self.right.sequence in item.major_sequences:
                return True
            
            raise KeyError( "I cannot find the component '{}' within this edge. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
        elif isinstance( item, bool ):
            return item
        else:
            raise SwitchError( "position.item", item, instance = True )
    
    
    def sides( self, item: TSide ) -> Tuple["LegoSubsequence", "LegoSubsequence"]:
        """
        As `sides` but returns both items.
        """
        position = self.position( item )
        return (self.right, self.left) if position else (self.left, self.right)
    
    
    def side( self, item: TSide, opposite = False ) -> "LegoSubsequence":
        """
        Returns the side of the given item.
        :param item:        See `position` for accepted values. 
        :param opposite:    When `true` the side opposing `item` is returned. 
        :return:            The requested side. 
        """
        position = self.position( item )
        
        if opposite:
            position = not position
        
        return self.right if position else self.left
    
    
    def opposite( self, item: TSide ) -> "LegoSubsequence":
        """
        Convenience function that calls `side` with `opposite = True`.
        """
        return self.side( item, opposite = True )


class LegoSubsequence( IHasFasta ):
    """
    Portion of a sequence
    """
    
    
    def __init__( self, sequence: "LegoSequence", start: int, end: int ):
        """
        CONSTRUCTOR
        :param sequence: Owning sequence
        :param start: Leftmost position (inclusive) 
        :param end: Rightmost position (inclusive) 
        """
        assert isinstance( sequence, LegoSequence )
        assert isinstance( start, int )
        assert isinstance( end, int )
        
        assert start >= 1
        assert end >= 1
        
        if start > end:
            raise ValueError( "Attempt to create a subsequence in «{0}» where start ({1}) > end ({2}).".format( sequence, start, end ) )
        
        self.sequence: LegoSequence = sequence
        self.__start: int = start  # Start position
        self.__end: int = end  # End position
    
    
    def to_fasta( self ):
        fasta = []
        
        fasta.append( ">" + self.sequence.accession + "[{}:{}]".format( self.start, self.end ) )
        
        if self.site_array is not None:
            fasta.append( self.site_array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    @classmethod
    def merge_list( cls, source: List["LegoSubsequence"] ):
        """
        Merges together adjacent subsequences in the same sequence.
        :param source:  Input list of subsequences, the list is directly modified. 
        :return:        The source list, after modification. 
        """
        processing = True
        
        while processing:
            processing = False
            
            for a in source:
                for b in source:
                    if a is not b and a.sequence is b.sequence and a.end + 1 == b.start:
                        source.remove( a )
                        source.remove( b )
                        source.append( cls( a.sequence, a.start, b.end ) )
                        processing = True
                        break
                
                if processing:
                    break
        
        return source
    
    
    @classmethod
    def list_union( cls, options: List["LegoSubsequence"] ):
        """
        Returns a `LegoSubsequence` that encompasses all `LegoSubsequence`s in the list.
        """
        if not options:
            raise ValueError( "Cannot obtain a union of subsequences for an empty list." )
        
        a = options[0]
        
        for i in range( 1, len( options ) ):
            a = a.union( options[i] )
        
        return a
    
    
    def has_overlap( self, two: "LegoSubsequence" ) -> bool:
        """
        Returns if the `two` `LegoSubsequence`s overlap.
        """
        if self.sequence is not two.sequence:
            return False
        
        return self.start <= two.end and two.start <= self.end
    
    
    def has_encompass( self, two: "LegoSubsequence" ) -> bool:
        """
        Returns if the first of the `two` `LegoSubsequence`s encompasses the other.
        """
        if self.sequence is not two.sequence:
            return False
        
        return self.start <= two.start and self.end >= two.end
    
    
    def union( self, two: "LegoSubsequence" ) -> "LegoSubsequence":
        """
        Returns a `LegoSubsequence` that is the union of the `two`.
        If the `two` do not overlap the result is undefined.
        """
        assert self.sequence is two.sequence
        return LegoSubsequence( self.sequence, min( self.start, two.start ), max( self.end, two.end ) )  # todo: doesn't account for non-overlapping ranges
    
    
    def intersection( self, two: "LegoSubsequence" ) -> "LegoSubsequence":
        """
        Returns a `LegoSubsequence` that is the intersection of the `two`.
        :except NotFoundError: The `two` do not overlap.
        """
        assert self.sequence is two.sequence
        
        start = max( self.start, two.start )
        end = min( self.end, two.end )
        
        if start > end:
            raise NotFoundError( "Cannot create `intersection` for non-overlapping ranges «{}» and «{}».".format( self, two ) )
        
        return LegoSubsequence( self.sequence, start, end )
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Subsequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.RED,
                       icon = intermake_resources.folder,
                       extra = { "sequence": self.sequence,
                                 "start"   : self.start,
                                 "end"     : self.end,
                                 "length"  : self.length,
                                 "sites"   : self.site_array } )
    
    
    @staticmethod
    def to_string( sequence, start, end ) -> str:
        return "{}[{}:{}({})]".format( sequence.accession, start, end, end - start + 1 )
    
    
    def __str__( self ) -> str:
        return self.to_string( self.sequence, self.start, self.end )
    
    
    @property
    def start( self ) -> int:
        return self.__start
    
    
    @property
    def end( self ) -> int:
        return self.__end
    
    
    @start.setter
    def start( self, value: int ) -> None:
        assert isinstance( value, int )
        
        if not (0 < value <= self.__end):
            raise ValueError( "Attempt to set `start` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__start = value
    
    
    @end.setter
    def end( self, value: int ) -> None:
        assert isinstance( value, int )
        
        if not (self.__start <= value):
            raise ValueError( "Attempt to set `end` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__end = value
    
    
    @property
    def site_array( self ) -> Optional[str]:
        """
        Obtains the slice of the sequence array pertinent to this subsequence
        """
        if self.sequence.site_array:
            result = self.sequence.site_array[self.start - 1:self.end]
            if len( result ) != self.length:
                raise ValueError( "Cannot extract site range {}-{} from site array of length {}.".format( self.start, self.length, self.sequence.length ) )
            
            return result
        else:
            return None
    
    
    @property
    def length( self ) -> int:
        """
        Calculates the length of this subsequence
        """
        return self.end - self.start + 1


class LegoUserDomain( LegoSubsequence, ILegoSelectable ):
    """
    A user-domain is just domain (LegoSubsequence) which the user has defined.
    """
    pass


class LegoSequence( ILegoNode, ILegoSelectable, IHasFasta ):
    """
    Protein (or DNA) sequence
    
    :attr id:           Internal ID. An arbitrary number guaranteed to be unique within the model.
    :attr accession:    Database accession. Note that this can't look like an accession produced by the `legacy_accession` property.
    :attr model:        Owning model.
    :attr site_array:   Site data. This can be `None` before the data is loaded in. The length must match `length`.
    :attr comments:     Comments on the sequence.
    :attr length:       Length of the sequence. This must match `site_array`, it that is set.
    """
    
    # Formats for finding and creating legacy accessions
    _LEGACY_IDENTIFIER = re.compile( "^GrtS([0-9]+)$" )
    _LEGACY_FORMAT = "GrtS{}"
    
    
    def __init__( self, model: "LegoModel", accession: str, id: int ) -> None:
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions.
        """
        if LegoSequence.is_legacy_accession( accession ):
            raise ValueError( "You have a sequence with an accession «{}», but {} has reserved that name for compatibility with legacy Phylip format files. Avoid using accessions that only contain numbers prefixed by an 'S'.".format( accession, MENV.name ) )
        
        self.id: int = id
        self.accession: str = accession  # Database accession (ID)
        self.model: "LegoModel" = model
        self.site_array: str = None
        self.comments: List[str] = []
        self.length = 1
        self.position = EPosition.NONE
    
    
    def iter_edges( self ):
        return (x for x in self.model.edges if x.left is self or x.right is self)
    
    
    def iter_userdomains( self ):
        return (x for x in self.model.user_domains if x.sequence is self)
    
    
    @property
    def is_positioned( self ):
        return self.position != EPosition.NONE
    
    
    def to_fasta( self ):
        fasta = []
        
        fasta.append( ">" + self.accession )
        
        if self.site_array:
            fasta.append( self.site_array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    @staticmethod
    def read_legacy_accession( name: str ) -> int:
        return int( LegoSequence._LEGACY_IDENTIFIER.match( name ).groups()[0] )
    
    
    @staticmethod
    def is_legacy_accession( name: str ):
        """
        Determines if an accession was created via the `legacy_accession` function.
        """
        return bool( LegoSequence._LEGACY_IDENTIFIER.match( name ) )
    
    
    @property
    def legacy_accession( self ):
        """
        We make an accession for compatibility with programs that still use Phylip format.
        We can't just use a number because some programs mistake this for a line count.
        """
        return self._LEGACY_FORMAT.format( self.id )
    
    
    def get_totality( self ) -> LegoSubsequence:
        """
        Gets the subsequence spanning the totality of this sequence.
        """
        return LegoSubsequence( self, 1, self.length )
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        return UiInfo( name = self.accession,
                       comment = "",
                       type_name = "Sequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.BLUE,
                       icon = intermake_resources.folder,
                       extra = { "id"       : self.legacy_accession,
                                 "length"   : self.length,
                                 "accession": self.accession,
                                 "position" : self.position,
                                 "num_sites": len( self.site_array ) if self.site_array else "?",
                                 "sites"    : self.site_array } )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return "G{}".format( self.accession or self.index )
    
    
    @property
    def index( self ) -> int:
        """
        Gets the index of this sequence within the model
        """
        return self.model.sequences.index( self )
    
    
    def __repr__( self ) -> str:
        """
        OVERRIDE 
        """
        return "{}".format( self.accession )
    
    
    def _ensure_length( self, new_length: int ) -> None:
        """
        Ensures the length of the sequence accommodates `new_length`.
        """
        assert isinstance( new_length, int )
        
        if new_length == 0:
            return
        
        if self.length < new_length:
            self.length = new_length
    
    
    def sub_sites( self, start: int, end: int ) -> Optional[str]:
        """
        Retrieves a portion of the sequence.
        Indices are 1 based and inclusive.
        
        :param start:       Start index 
        :param end:         End index 
        :return:            Substring, or `None` if no site array is available. 
        """
        if self.site_array is None:
            return None
        
        assert start <= end, "{} {}".format( start, end )
        assert 0 < start <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        assert 0 < end <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        
        return self.site_array[start:end]


_GREEK = "αβγδϵζηθικλμνξοπρστυϕχψω"


class INamedGraph( ILegoSelectable ):
    @property
    def graph( self ) -> Optional[MGraph]:
        return self.on_get_graph()
    
    
    def on_get_graph( self ) -> Optional[MGraph]:
        raise NotImplementedError( "abstract" )
    
    
    @property
    def name( self ) -> str:
        return self.on_get_name()
    
    
    def on_get_name( self ) -> str:
        return str( self )


class UserGraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ) -> str:
        return self.__name
    
    
    def __init__( self, graph: MGraph, name = "user_graph" ):
        assert isinstance( graph, MGraph )
        assert isinstance( name, str )
        self.__graph = graph
        self.__name = name
    
    
    def __str__( self ):
        return self.name


class LegoComponent( INamedGraph, IHasFasta ):
    """
    Stores information about a component of the (:class:`LegoModel`).
    
    :attr model:                      Back-reference to model
    :attr index:                      Index of component within model
    :attr tree:                       Tree generated for this component.
                                      Set during the tree stage and `None` before.
    :attr alignment:                  Alignment generated for this component, in FASTA format, with sequences
                                      referenced by IID (not accession).
                                      Set during the alignment stage and `None` before.
    :attr major_sequences:            Major sequences of this component.
                                      i.e. sequences only containing domains in :attr:`minor_subsequences`
    :attr minor_subsequences:         Minor subsequences of this component.
                                      i.e. all domains in this component.
    :attr splits:                     Splits of the component tree.
                                      Calculated during the NRFG stage and `None` before.
    :attr leaves:                     Leaves used in `splits`.
                                      Calculated during the NRFG stage and `None` before.       
    """
    
    
    def __init__( self, model: "LegoModel", index: int, major_sequences: List[LegoSequence] ):
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions.
        """
        self.model: LegoModel = model
        self.index: int = index
        self.alignment: str = None
        self.major_sequences: List[LegoSequence] = major_sequences
        self.minor_subsequences: List[LegoSubsequence] = None
        self.splits: FrozenSet[LegoSplit] = None
        self.leaves: FrozenSet[ILegoNode] = None
        self.tree: MGraph = None
        self.tree_unrooted: MGraph = None
        self.tree_newick: str = None
    
    
    def get_accid( self ):
        for x in sorted( self.major_sequences, key = cast( Any, str ) ):
            return x.accession
    
    
    @property
    def named_tree( self ):
        return _ComponentAsGraph( self, False )
    
    
    @property
    def named_tree_unrooted( self ):
        return _ComponentAsGraph( self, True )
    
    
    def to_details( self ):
        r = []
        r.append( "MAJOR-SE: {}".format( string_helper.format_array( self.major_sequences, sort = True ) ) )
        r.append( "MINOR-SE: {}".format( string_helper.format_array( self.minor_sequences, sort = True ) ) )
        r.append( "MINOR-SS: {}".format( string_helper.format_array( self.minor_subsequences ) ) )
        r.append( "INCOMING: {}".format( string_helper.format_array( self.incoming_components(), sort = True ) ) )
        r.append( "OUTGOING: {}".format( string_helper.format_array( self.outgoing_components(), sort = True ) ) )
        return "\n".join( r )
    
    
    def get_alignment_fasta( self ):
        r = []
        
        for name, value in bio_helper.parse_fasta( text = self.alignment ):
            r.append( ">" + self.model.find_sequence_by_legacy_accession( name ).accession )
            r.append( value )
        
        return "\n".join( r )
    
    
    def to_fasta( self ):
        fasta = []
        
        for subsequence in self.minor_subsequences:
            fasta.append( ">{}[{}:{}]".format( subsequence.sequence.accession, subsequence.start, subsequence.end ) )
            fasta.append( subsequence.site_array )
            fasta.append( "" )
        
        return "\n".join( fasta )
    
    
    def to_legacy_fasta( self ):
        fasta = []
        
        for subsequence in self.minor_subsequences:
            fasta.append( ">{}".format( subsequence.sequence.legacy_accession ) )
            fasta.append( subsequence.site_array )
            fasta.append( "" )
        
        return "\n".join( fasta )
    
    
    def on_get_graph( self ):
        return self.tree
    
    
    def on_get_name( self ):
        return str( self )
    
    
    def get_alignment_by_accession( self ) -> str:
        """
        Gets the `alignment` property, but translates sequence IDs into accessions
        """
        if not self.alignment:
            return self.alignment
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE
        """
        return UiInfo( name = str( self ),
                       comment = str( self.__doc__ ),
                       type_name = "Component",
                       value = "{} sequences".format( array_helper.count( self.major_sequences ) ),
                       colour = EColour.RED,
                       icon = intermake_resources.folder,
                       extra = { "index"      : self.index,
                                 "major"      : self.major_sequences,
                                 "minor_s"    : self.minor_sequences,
                                 "minor_ss"   : self.minor_subsequences,
                                 "alignment"  : self.alignment,
                                 "tree"       : self.tree,
                                 "tree_newick": self.tree_newick,
                                 "incoming"   : self.incoming_components(),
                                 "outgoing"   : self.outgoing_components() } )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return "comp_{}".format( self.get_accid() )
    
    
    def incoming_components( self ) -> List["LegoComponent"]:
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.minor_sequences for x in self.major_sequences ) and component is not self]
    
    
    def outgoing_components( self ) -> List["LegoComponent"]:
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.major_sequences for x in self.minor_sequences ) and component is not self]
    
    
    @property
    def minor_sequences( self ) -> List[LegoSequence]:
        """
        Returns the minor sequences.
        Sequences with at least one subsequence in the minor set.
        See `__detect_minor` for the definition.
        """
        return list( set( subsequence.sequence for subsequence in self.minor_subsequences ) )
    
    
    def get_minor_subsequence_by_sequence( self, sequence: LegoSequence ) -> LegoSubsequence:
        for subsequence in self.minor_subsequences:
            if subsequence.sequence is sequence:
                return subsequence
        
        raise NotFoundError( "Sequence «{}» not in component «{}».".format( sequence, self ) )


class ComponentAsData:
    def __init__( self, component: "LegoComponent" ):
        self.component = component
    
    
    def visualisable_info( self ):
        return self.component.visualisable_info()
    
    
    def __str__( self ):
        return "{}::data".format( self.component )


class FusionGraph( INamedGraph ):
    def __init__( self, graph, is_clean ):
        self.__graph = graph
        self.is_clean = is_clean
    
    
    def on_get_graph( self ):
        return self.__graph
    
    
    def on_get_name( self ):
        return str( self )
    
    
    def __str__( self ):
        return "nrfg" if self.is_clean else "nrfg_unclean"


class Subgraph( INamedGraph ):
    
    
    def __init__( self, graph: MGraph, subset: "LegoSubset", algorithm: str ):
        """
        CONSTRUCTOR
        :param graph:       The actual graph 
        :param subset:      The subset from whence it came 
        :param algorithm:   The algorithm used to generate the graph 
        """
        self.__graph = graph
        self.__subset = subset
        self.__algorithm = algorithm
    
    
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ) -> str:
        return str( self )
    
    
    def __str__( self ):
        return "subgraph_{}".format( self.__subset.get_accid() )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       value = str( self.graph ),
                       extra = { "algorithm": self.__algorithm } )


class ComponentAsAlignment( IHasFasta ):
    def __init__( self, component: "LegoComponent" ):
        self.component = component
    
    
    def visualisable_info( self ):
        return self.component.visualisable_info()
    
    
    def to_fasta( self ):
        return self.component.get_alignment_fasta()
    
    
    def __str__( self ):
        return "{}::alignment".format( self.component )


class _ComponentAsGraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        if self.unrooted:
            return self.component.tree_unrooted
        else:
            return self.component.tree
    
    
    def on_get_name( self ) -> str:
        return str( self )
    
    
    def __init__( self, component: "LegoComponent", unrooted = False ):
        self.component = component
        self.unrooted = unrooted
    
    
    def visualisable_info( self ):
        x = self.component.visualisable_info()
        x.name = str( self )
        return x
    
    
    def to_fasta( self ):
        return self.component.get_alignment_fasta()
    
    
    def __str__( self ):
        return "{}_{}".format( self.component, "unrooted" if self.unrooted else "tree" )


class LegoEdgeCollection:
    """
    The collection of edges, held by the model.
    
    :attr __model:          Owning model.
    :attr __edges:          Edge list
    :attr __by_sequence:    Lookup table, sequence to edge list.
    """
    
    
    def __init__( self, model: "LegoModel" ):
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions. 
        """
        self.__model = model
        self.__edges: List[LegoEdge] = []
        self.__by_sequence: Dict[LegoSequence, List[LegoEdge]] = { }
    
    
    def __bool__( self ):
        return bool( self.__edges )
    
    
    def __len__( self ):
        return len( self.__edges )
    
    
    def __iter__( self ):
        return iter( self.__edges )
    
    
    def __str__( self ):
        return "{} edges".format( len( self ) )
    
    
    def find_sequence( self, sequence: LegoSequence ) -> List[LegoEdge]:
        return self.__by_sequence.get( sequence, [] )
    
    
    def add( self, edge: LegoEdge ):
        self.__edges.append( edge )
        array_helper.add_to_listdict( self.__by_sequence, edge.left.sequence, edge )
        array_helper.add_to_listdict( self.__by_sequence, edge.right.sequence, edge )
    
    
    def remove( self, edge: LegoEdge ):
        self.__edges.remove( edge )
        array_helper.remove_from_listdict( self.__by_sequence, edge.left.sequence, edge )
        array_helper.remove_from_listdict( self.__by_sequence, edge.right.sequence, edge )


class LegoComponentCollection:
    def __init__( self, model: "LegoModel" ):
        self.__model = model
        self.__components: List[LegoComponent] = []
    
    
    @property
    def count( self ):
        return len( self )
    
    
    @property
    def num_aligned( self ):
        return sum( x.alignment is not None for x in self )
    
    
    @property
    def num_trees( self ):
        return sum( x.graph is not None for x in self )
    
    
    def __bool__( self ):
        return bool( self.__components )
    
    
    def add( self, component: LegoComponent ):
        assert isinstance( component, LegoComponent ), component
        self.__components.append( component )
    
    
    def __getitem__( self, item ):
        return self.__components[item]
    
    
    def __len__( self ):
        return len( self.__components )
    
    
    @property
    def is_empty( self ):
        return len( self.__components ) == 0
    
    
    def find_components_for_minor_subsequence( self, subsequence: LegoSubsequence ) -> List[LegoComponent]:
        r = []
        
        for component in self:
            for minor_subsequence in component.minor_subsequences:
                if minor_subsequence.has_overlap( subsequence ):
                    r.append( component )
                    break
        
        return r
    
    
    def find_components_for_minor_sequence( self, sequence: LegoSequence ) -> List[LegoComponent]:
        r = []
        
        for component in self:
            for minor_subsequence in component.minor_subsequences:
                if minor_subsequence.sequence is sequence:
                    r.append( component )
                    break
        
        return r
    
    
    def find_component_for_major_sequence( self, sequence: LegoSequence ) -> LegoComponent:
        for component in self.__components:
            if sequence in component.major_sequences:
                return component
        
        raise NotFoundError( "Sequence «{}» does not have a component.".format( sequence ) )
    
    
    def find_component_by_name( self, name: str ) -> LegoComponent:
        for component in self.__components:
            if str( component ) == name:
                return component
        
        raise NotFoundError( "Cannot find the component with the name «{}».".format( name ) )
    
    
    def has_sequence( self, sequence: LegoSequence ) -> bool:
        try:
            self.find_component_for_major_sequence( sequence )
            return True
        except NotFoundError:
            return False
    
    
    def __iter__( self ) -> Iterator[LegoComponent]:
        return iter( self.__components )
    
    
    def __str__( self ):
        return "{} components".format( len( self.__components ) )
    
    
    def clear( self ):
        self.__components.clear()


class LegoSequenceCollection:
    def __init__( self, model: "LegoModel" ):
        self.__model = model
        self.__sequences: List[LegoSequence] = []
    
    
    @property
    def num_fasta( self ):
        return sum( x.site_array is not None for x in self )
    
    
    def to_fasta( self ):
        r = []
        
        for s in self:
            r.append( s.to_fasta() )
        
        return "\n".join( r )
    
    
    def __bool__( self ):
        return bool( self.__sequences )
    
    
    def __len__( self ):
        return len( self.__sequences )
    
    
    def __iter__( self ) -> Iterator[LegoSequence]:
        return iter( self.__sequences )
    
    
    def __str__( self ):
        return "{} sequences".format( len( self ) )
    
    
    def add( self, sequence: LegoSequence ):
        if any( x.accession == sequence.accession for x in self.__sequences ):
            raise ValueError( "Cannot add a sequence «{}» to the model because its accession is already in use.".format( sequence ) )
        
        array_helper.ordered_insert( self.__sequences, sequence, lambda x: x.accession )
    
    
    def index( self, sequence: LegoSequence ):
        return self.__sequences.index( sequence )


class LegoUserDomainCollection:
    def __init__( self, model: "LegoModel" ):
        self.__model = model
        self.__user_domains: List[LegoUserDomain] = []
        self.__by_sequence: Dict[LegoSequence, List[LegoUserDomain]] = { }
    
    
    def add( self, domain: LegoUserDomain ):
        self.__user_domains.append( domain )
        
        if domain.sequence not in self.__by_sequence:
            self.__by_sequence[domain.sequence] = []
        
        self.__by_sequence[domain.sequence].append( domain )
    
    
    def clear( self ):
        self.__user_domains.clear()
        self.__by_sequence.clear()
    
    
    def __bool__( self ):
        return bool( self.__user_domains )
    
    
    def __len__( self ):
        return len( self.__user_domains )
    
    
    def __iter__( self ) -> Iterator[LegoUserDomain]:
        return iter( self.__user_domains )
    
    
    def by_sequence( self, sequence: LegoSequence ) -> Iterable[LegoUserDomain]:
        list = self.__by_sequence.get( sequence )
        
        if list is None:
            return [LegoUserDomain( sequence, 1, sequence.length )]
        else:
            return list


class LegoViewOptions:
    """
    Options on the lego view
    
    :attr y_snap:                      Snap movements to the Y axis (yes | no | when no alt)
    :attr x_snap:                      Snap movements to the X axis (yes | no | when no alt)
    :attr move_enabled:                Allow movements (yes | no | when double click)
    :attr view_piano_roll:             View piano roll (yes | no | when selected)
    :attr view_names:                  View sequence names (yes | no | when selected)
    :attr view_positions:              View domain positions (yes | no | when selected)
    :attr view_components:             View domain components (yes | no | when selected)
    :attr mode:                        Edit mode
    :attr domain_function:             Domain generator
    :attr domain_function_parameter:   Parameter passed to domain generator (domain_function dependent)
    :attr domain_positions:            Positions of the domains on the screen - maps (id, site) --> (x, y)
    """
    
    
    def __init__( self ):
        self.y_snap: TTristate = None
        self.x_snap: TTristate = None
        self.move_enabled: TTristate = None
        self.view_piano_roll: TTristate = None
        self.view_names: TTristate = True
        self.view_positions: TTristate = None
        self.view_components: TTristate = None
        self.mode = EMode.SEQUENCE
        self.domain_positions: Dict[Tuple[int, int], Tuple[int, int]] = { }


class LegoSplit( ILegoSelectable ):
    """
    Wraps a :class:`Split` making it Groot-friendly.
    """
    
    
    def __init__( self, split: Split, index: int ):
        self.split = split
        self.index = index
        self.components: Set[LegoComponent] = set()
        self.evidence_for: FrozenSet[LegoComponent] = None
        self.evidence_against: FrozenSet[LegoComponent] = None
        self.evidence_unused: FrozenSet[LegoComponent] = None
    
    
    def __str__( self ):
        return "Split{}".format( self.index )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Split",
                       value = self.split.to_string(),
                       colour = EColour.CYAN,
                       icon = groot_resources.black_split,
                       extra = { "inside"          : self.split.inside,
                                 "outside"         : self.split.outside,
                                 "components"      : self.components,
                                 "evidence_for"    : self.evidence_for,
                                 "evidence_against": self.evidence_against,
                                 "evidence_unused" : self.evidence_unused,
                                 } )
    
    
    def __eq__( self, other ):
        if isinstance( other, LegoSplit ):
            return self.split == other.split
        elif isinstance( other, Split ):
            return self.split == other
        else:
            return False
    
    
    def __hash__( self ):
        return hash( self.split )
    
    
    def is_evidenced_by( self, other: "LegoSplit" ) -> TTristate:
        """
        A split is evidenced by an `other` if it is a subset of the `other`.
        No evidence can be provided if the `other` set of leaves is not a subset
        
        :return: TTristate where:
                    True = Supports
                    False = Rejects
                    None = Cannot evidence 
        """
        if not self.split.all.issubset( other.split.all ):
            return None
        
        return self.split.inside.issubset( other.split.inside ) and self.split.outside.issubset( other.split.outside ) \
               or self.split.inside.issubset( other.split.inside ) and self.split.outside.issubset( other.split.outside )


class NrfgReport( ILegoSelectable ):
    def __init__( self ):
        pass
    
    
    def __str__( self ):
        return "Report"
    
    
    def visualisable_info( self ):
        return UiInfo( name = "report",
                       comment = "",
                       type_name = "Report",
                       value = "Pass",
                       colour = EColour.GREEN,
                       icon = groot_resources.black_check )


class LegoSubset( ILegoSelectable, IVisualisable ):
    """
    Represents a subset of leaf nodes (see `ILeaf`).
    """
    
    
    def __init__( self, model: "LegoModel", index: int, contents: FrozenSet[ILegoNode] ):
        self.model = model
        self.index = index
        self.contents = contents
        self.pregraphs: List[LegoPregraph] = None
    
    
    def get_accid( self ):
        for x in sorted( self.contents, key = cast( Any, str ) ):
            if isinstance( x, LegoSequence ):
                return x.accession
        
        return self.index
    
    
    def __len__( self ):
        return len( self.contents )
    
    
    def __str__( self ):
        return "subset_{}".format( self.get_accid() )
    
    
    def get_details( self ):
        return string_helper.format_array( self.contents )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Subset",
                       value = self.get_details(),
                       colour = EColour.CYAN,
                       icon = groot_resources.black_subset,
                       extra_indexed = self.contents )


class ModelStatus:
    def __init__( self, model: "LegoModel", stage: LegoStage ):
        self.model: LegoModel = model
        self.stage: LegoStage = stage
    
    
    def assert_drop( self ):
        if self.is_none:
            raise NotReadyError( "Cannot drop «{}» stage because this data does not yet exist.".format( self.stage ) )
        
        for stage in constants.STAGES:
            if stage.requires == self:
                raise InUseError( "Cannot drop «{}» stage the following stage, «{}» is relying on that data. Perhaps you meant to drop that stage first?".format( self.stage, stage ) )
    
    
    def assert_create( self ):
        if self.is_complete:
            raise NotReadyError( "Cannot create «{}» stage because this data already exists.".format( self.stage ) )
        
        if self.stage.requires is not None:
            req = self.model.get_status( self.stage.requires )
            
            if req.is_not_complete:
                raise NotReadyError( "Cannot create «{}» because the preceding stage «{}» is not complete. Perhaps you meant to complete that stage first?".format( self.stage, self.stage.requires ) )
    
    
    @property
    def requisite_complete( self ) -> bool:
        return self.stage.requires is None or ModelStatus( self.model, self.stage.requires ).is_complete
    
    
    def __bool__( self ):
        return self.is_complete
    
    
    def __str__( self ):
        if self.is_complete:
            return self.get_headline_text() or "(complete)"
        if self.is_partial:
            return "(partial) " + self.get_headline_text()
        else:
            return "(no data)"
    
    
    def get_headline_text( self ):
        return self.stage.headline( self.model ) if self.stage.headline is not None else ""
    
    
    @property
    def is_none( self ):
        return not self.is_partial
    
    
    @property
    def is_partial( self ):
        return any( self.get_elements() )
    
    
    def get_elements( self ):
        r = self.stage.status( self.model )
        if r is None:
            return ()
        return r
    
    
    @property
    def is_not_complete( self ):
        return not self.is_complete
    
    
    @property
    def is_complete( self ):
        has_any = False
        
        for element in self.get_elements():
            if element:
                has_any = True
            else:
                return False
        
        return has_any


class LegoFusion( ILegoSelectable, IVisualisable ):
    """
    Describes a fusion event
    
    :data component_a:          First component
    :data component_b:          Second component
    :data products:             Generated component (root)
    :data future_products:      Generated component (all possibilities)
    :data point_a:              The name of the node on the first component which the fusion occurs
    :data point_b:              The name of the node on the second component which the fusion occurs
    """
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Fusion",
                       value = self.long_name,
                       colour = EColour.RED,
                       icon = groot_resources.black_fusion,
                       extra = { "index"          : self.index,
                                 "component_a"    : self.component_a,
                                 "component_b"    : self.component_b,
                                 "products"       : self.products,
                                 "future_products": self.future_products,
                                 "formations"     : self.formations } )
    
    
    def __init__( self, index: int, component_a: LegoComponent, component_b: LegoComponent, intersections: Set[LegoComponent] ) -> None:
        if component_a is component_b:
            raise ValueError( "FusionEvent component A ({}) cannot be component B ({}).".format( component_a, component_b ) )
        
        if any( x is component_a or x is component_b for x in intersections ):
            raise ValueError( "FusionEvent intersections ({}) cannot contain component A ({}) or component B ({}).".format( string_helper.format_array( intersections ), component_a, component_b ) )
        
        self.index = index
        self.component_a: LegoComponent = component_a
        self.component_b: LegoComponent = component_b
        self.products: Set[LegoComponent] = intersections
        self.future_products: Set[LegoComponent] = set( intersections )
        self.formations: List[LegoFormation] = []
    
    
    @property
    def component_c( self ) -> LegoComponent:
        return array_helper.single_or_error( self.products )
    
    
    @property
    def long_name( self ):
        return "({}+{}={})".format( self.component_a, self.component_b, ",".join( x.__str__() for x in self.products ) )
    
    
    def __repr__( self ):
        return "F" + str( self.get_accid() )
    
    
    def get_accid( self ):
        return self.component_c.get_accid()


class LegoFormation( IVisualisable, ILegoNode ):
    
    
    def __init__( self,
                  event: LegoFusion,
                  component: LegoComponent,
                  sequences: Set[ILegoNode],
                  index: int ):
        self.event = event
        self.component = component
        self.sequences = sequences
        self.pertinent_inner = frozenset( self.sequences.intersection( self.event.component_c.major_sequences ) )
        self.points: List[LegoPoint] = []
        self.index = index
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = str( self ),
                       type_name = "Formation",
                       value = "{} points".format( len( self.points ) ),
                       extra = {
                           "component"      : self.component,
                           "sequences"      : self.sequences,
                           "pertinent_inner": self.pertinent_inner,
                           "index"          : self.index,
                           "points"         : self.points } )
    
    
    def __repr__( self ):
        return "{}.{}".format( self.event, self.index )
    
    
    _LEGACY_IDENTIFIER = re.compile( "^GrtF([0-9]+)F([0-9]+)$" )
    _LEGACY_FORMAT = "GrtF{}F{}"
    
    
    @property
    def legacy_accession( self ):
        return self._LEGACY_FORMAT.format( self.event.index, self.index )
    
    
    @classmethod
    def read_legacy_accession( cls, name: str ) -> Tuple[int, int]:
        g = cls._LEGACY_IDENTIFIER.match( name ).groups()
        return int( g[0] ), int( g[1] )
    
    
    @classmethod
    def is_legacy_accession( cls, name: str ):
        """
        Determines if an accession was created via the `legacy_accession` property.
        """
        return bool( cls._LEGACY_IDENTIFIER.match( name ) )


class LegoPoint( ILegoNode, ILegoSelectable, IVisualisable ):
    """
    Point of fusion.
    
    :attr event:            Participating event
    :attr component:        The component tree this point resides within
    :attr sequences:        The genes this fusion point _creates_
    :attr outer_sequences:  A subset of genes from which this fusion point _originates_
    """
    
    
    # Formats for finding and creating legacy accessions
    
    def __init__( self,
                  formation: LegoFormation,
                  outer_sequences: Set[ILegoNode],
                  index: int ):
        self.formation = formation
        self.outer_sequences = outer_sequences
        self.pertinent_outer = frozenset( self.outer_sequences.intersection( set( self.formation.event.component_a.major_sequences ).union( set( self.formation.event.component_b.major_sequences ) ) ) )
        self.index = index
    
    
    def __repr__( self ):
        return "{}.{}".format( self.formation, self.index )
    
    
    @property
    def component( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.component
    
    
    @property
    def sequences( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.sequences
    
    
    @property
    def pertinent_inner( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.pertinent_inner
    
    
    @property
    def event( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.event
    
    
    _LEGACY_IDENTIFIER = re.compile( "^GrtP([0-9]+)P([0-9]+)P([0-9]+)$" )
    _LEGACY_FORMAT = "GrtP{}P{}P{}"
    
    
    @property
    def legacy_accession( self ):
        return self._LEGACY_FORMAT.format( self.formation.event.index, self.formation.index, self.index )
    
    
    @classmethod
    def read_legacy_accession( cls, name: str ) -> Tuple[int, int, int]:
        g = cls._LEGACY_IDENTIFIER.match( name ).groups()
        return int( g[0] ), int( g[1] ), int( g[2] )
    
    
    @classmethod
    def is_legacy_accession( cls, name: str ):
        """
        Determines if an accession was created via the `legacy_accession` property.
        """
        return bool( cls._LEGACY_IDENTIFIER.match( name ) )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       comment = "",
                       value = "{} sequences".format( len( self.formation.sequences ) ),
                       colour = EColour.MAGENTA,
                       icon = groot_resources.black_fusion,
                       type_name = "Point",
                       extra = {
                           "outer_sequences": self.outer_sequences,
                           "pertinent_outer": self.pertinent_outer,
                           "index"          : self.index } )
    
    
    @property
    def count( self ):
        return len( self.formation.sequences )
    
    
    def get_pertinent_inner( self ):
        return self.formation.pertinent_inner.union( { self } )
    
    
    def get_pertinent_outer( self ):
        return self.pertinent_outer.union( { self } )


class LegoFusionEventCollection:
    def __init__( self ):
        self.events: List[LegoFusion] = []
    
    
    def add( self, item: LegoFusion ):
        self.events.append( item )
    
    
    def clear( self ):
        self.events.clear()
    
    
    def __len__( self ):
        return len( self.events )
    
    
    def __iter__( self ):
        return iter( self.events )
    
    
    def __bool__( self ):
        return bool( self.events )
    
    
    @property
    def num_points( self ):
        return sum( sum( y.points.__len__() for y in x.formations ) for x in self )


class FixedUserGraph( UserGraph ):
    """
    :class:`UserGraph` that has been saved by the user to the :class:`LegoUserGraphCollection` at :field:`LegoModel.user_graphs`.
    """
    pass


class LegoUserGraphCollection:
    def __init__( self, model: "LegoModel" ):
        self.__model = model
        self.__contents = []
    
    
    def __len__( self ):
        return len( self.__contents )
    
    
    def append( self, graph: FixedUserGraph ):
        exception_helper.assert_type( "graph", graph, FixedUserGraph )
        
        for graph2 in self.__model.iter_graphs():
            if graph2.name == graph.name:
                raise ValueError( "Your graph is called '{}' but there is already a graph with this name." )
        
        self.__contents.append( graph )
    
    
    def remove( self, graph: FixedUserGraph ):
        self.__contents.remove( graph )
    
    
    def __iter__( self ):
        return iter( self.__contents )


class LegoPregraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def __str__( self ):
        return "pregraph_{}_in_{}".format( self.subset.get_accid(), self.component.get_accid() )
    
    
    def __init__( self, graph: MGraph, subset: LegoSubset, component: LegoComponent ):
        self.__graph = graph
        self.subset = subset
        self.component = component


class LegoModel( IVisualisable ):
    """
    The model used by Groot.
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        Creates a new model with no data
        Use the `import_*` functions to add data from a file.
        """
        self.__incremental_id = 0
        self.sequences = LegoSequenceCollection( self )
        self.components = LegoComponentCollection( self )
        self.edges = LegoEdgeCollection( self )
        self.comments = ["MODEL CREATED AT {}".format( string_helper.current_time() )]
        self.__seq_type = ESiteType.UNKNOWN
        self.file_name = None
        self.fusion_events = LegoFusionEventCollection()
        self.ui_options = LegoViewOptions()
        self.user_domains = LegoUserDomainCollection( self )
        self.user_graphs = LegoUserGraphCollection( self )
        self.splits: FrozenSet[LegoSplit] = frozenset()
        self.consensus: FrozenSet[LegoSplit] = frozenset()
        self.fusion_graph_unclean: FusionGraph = None
        self.fusion_graph_clean: FusionGraph = None
        self.report: NrfgReport = None
        self.subsets: FrozenSet[LegoSubset] = frozenset()
        self.subgraphs: Sequence[Subgraph] = tuple()
        self.subgraphs_sources: Sequence[int] = tuple()
        self.subgraphs_destinations: Sequence[int] = tuple()
    
    
    def iter_pregraphs( self ) -> Iterable[LegoPregraph]:
        """
        Iterates through the model pregraphs.
        """
        for subset in self.subsets:  # type: LegoSubset
            if subset.pregraphs is not None:
                yield from subset.pregraphs
    
    
    @property
    def fusion_points( self ) -> Iterator[LegoPoint]:
        for event in self.fusion_events:
            for formation in event.formations:
                yield from formation.points
    
    
    def get_status( self, stage: LegoStage ) -> ModelStatus:
        return ModelStatus( self, stage )
    
    
    def has_any_tree( self ):
        return any( x.graph for x in self.components )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = self.__doc__,
                       type_name = "Model",
                       value = "{} sequences".format( len( self.sequences ) ),
                       colour = EColour.YELLOW,
                       icon = intermake_resources.folder,
                       extra = { "documentation"         : self.__doc__,
                                 "graphs"                : list( self.iter_graphs() ),
        
                                 "sequences"             : self.sequences,
                                 "components"            : self.components,
                                 "edges"                 : self.edges,
                                 "comments"              : self.comments,
                                 "site_type"             : self.site_type,
                                 "file_name"             : self.file_name,
                                 "fusion_events"         : self.fusion_events,
                                 "ui_options"            : self.ui_options,
                                 "user_domains"          : self.user_domains,
                                 "user_graphs"           : self.user_graphs,
                                 "splits"                : self.splits,
                                 "consensus"             : self.consensus,
                                 "fusion_graph_unclean"  : self.fusion_graph_unclean,
                                 "fusion_graph_clean"    : self.fusion_graph_clean,
                                 "report"                : self.report,
                                 "subsets"               : self.subsets,
                                 "pregraphs"             : self.iter_pregraphs(),
                                 "subgraphs"             : self.subgraphs,
                                 "subgraphs_sources"     : self.subgraphs_sources,
                                 "subgraphs_destinations": self.subgraphs_destinations,
        
                                 "results"               : MENV.host.last_results,
                                 "plugins"               : MENV.plugins.plugins() } )
    
    
    def __str__( self ):
        return self.name
    
    
    @property
    def name( self ) -> str:
        from groot.data import global_view
        if self is not global_view.current_model():
            return "Not the current model"
        
        if self.file_name:
            return FileHelper.get_filename_without_extension( self.file_name )
        elif self.sequences:
            return "Unsaved model"
        else:
            return "Empty model"
    
    
    @property
    def site_type( self ) -> ESiteType:
        """
        API
        Obtains the type of data in the model - protein, DNA or RNA.
        """
        if self.__seq_type != ESiteType.UNKNOWN:
            return self.__seq_type
        
        s = ESiteType.UNKNOWN
        
        for x in self.sequences:
            if x.site_array:
                for y in x.site_array:
                    if y not in "GAC":
                        if y == "T":
                            if s == ESiteType.UNKNOWN:
                                s = ESiteType.DNA
                        elif y == "U":
                            if s == ESiteType.UNKNOWN:
                                s = ESiteType.RNA
                        else:
                            s = ESiteType.PROTEIN
        
        self.__seq_type = s
        
        return s
    
    
    def _get_incremental_id( self ) -> int:
        """
        Obtains a unique identifier.
        """
        self.__incremental_id += 1
        return self.__incremental_id
    
    
    def _has_data( self ) -> bool:
        return bool( self.sequences )
    
    
    def find_sequence_by_accession( self, name: str ) -> "LegoSequence":
        for x in self.sequences:
            if x.accession == name:
                return x
        
        raise NotFoundError( "There is no sequence with the accession «{}».".format( name ) )
    
    
    def find_sequence_by_legacy_accession( self, name: str ) -> "LegoSequence":
        id = LegoSequence.read_legacy_accession( name )
        
        for x in self.sequences:
            if x.id == id:
                return x
        
        raise NotFoundError( "There is no sequence with the internal ID «{}».".format( id ) )
    
    
    def find_fusion_point_by_legacy_accession( self, name: str ) -> "LegoPoint":
        i_event, i_formation, i_point = LegoPoint.read_legacy_accession( name )
        
        for event in self.fusion_events:
            if event.index == i_event:
                for formation in event.formations:
                    if formation.index == i_formation:
                        for point in formation.points:
                            if point.index == i_point:
                                return point
        
        raise NotFoundError( "There is no fusion point with the internal ID «{}».".format( id ) )
    
    
    def find_fusion_formation_by_legacy_accession( self, name: str ) -> "LegoFormation":
        i_event, i_formation = LegoFormation.read_legacy_accession( name )
        
        for event in self.fusion_events:
            if event.index == i_event:
                for formation in event.formations:
                    if formation.index == i_formation:
                        return formation
        
        raise NotFoundError( "There is no fusion formation with the internal ID «{}».".format( id ) )
    
    
    def iter_graphs( self ):
        yield from (x.named_tree for x in self.components if x.tree is not None)
        yield from (x.named_tree_unrooted for x in self.components if x.tree_unrooted is not None)
        yield from self.subgraphs
        if self.fusion_graph_unclean:
            yield self.fusion_graph_unclean
        if self.fusion_graph_clean:
            yield self.fusion_graph_clean
        yield from self.user_graphs


# Obsolete names, do not use
FusionEvent = LegoFusion
FusionPoint = LegoPoint
