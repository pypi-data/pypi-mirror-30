from typing import List, Optional

from groot import algorithms
from groot.data import global_view
from groot.data.lego_model import LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command
from intermake.engine.environment import MCMD
from mhelper import string_helper


__mcmd_folder_name__ = "Generating"

@command()
def create_similarity( algorithm: str, evalue : Optional[float] = None, length: Optional[int] = None ) -> EChanges:
    """
    Creates the similarity matrix.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`. 
    :param evalue:      e-value cutoff. 
    :param length:      length cutoff. 
    """
    model = global_view.current_model()
    
    algorithms.s2_similarity.create_similarity( model, algorithm, evalue, length)
    
    MCMD.progress( "Similarities created, there are now {} edges.".format( len( model.edges ) ) )
    
    return EChanges.MODEL_ENTITIES

@command()
def create_domains( algorithm: str, param: int = 0 ) -> EChanges:
    """
    Creates the domains.
    Existing domains are always replaced.
    Domains are only used for viewing and have no bearing on the actual calculations.
    
    :param algorithm:   Mode of domain generation. See `algorithm_help`.
    :param param:       Parameter for mode. 
    """
    model = global_view.current_model()
    
    algorithms.s4_userdomains.create_userdomains( model, algorithm, param )
    
    MCMD.progress( "Domains created, there are now {} domains.".format( len( model.user_domains ) ) )
    
    return EChanges.DOMAINS


@command()
def create_components( major_tol: int = 0, minor_tol: Optional[int] = None, debug: bool = False ) -> EChanges:
    """
    Detects composites in the model.
    
    Requisites: Sequence similarity (BLAST data) must have been loaded
    
    :param major_tol:   Tolerance on overlap, in sites.
    :param minor_tol:   Tolerance on overlap, in sites. If `None` uses the `major_tol`.
    :param debug:       Internal parameter.
    """
    if minor_tol is None:
        minor_tol = major_tol
    
    model = global_view.current_model()
    
    if len( model.edges ) == 0:
        raise ValueError( "Refusing to make components because there is no edge data. Did you mean to load the edge data (BLAST) first?" )
    
    with MCMD.action( "Component detection" ):
        algorithms.s3_components.detect( model, major_tol, minor_tol, debug )
    
    for component in model.components:
        if len( component.major_sequences ) == 1:
            MCMD.warning( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}/{}?".format( major_tol, minor_tol ) )
            break
    
    MCMD.progress( "{} components detected.".format( len( model.components ) ) )
    
    return EChanges.COMPONENTS


@command()
def create_alignments( algorithm: Optional[str] = None, component: Optional[List[LegoComponent]] = None ) -> EChanges:
    """
    Aligns the component. If no component is specified, aligns all components.
    
    Requisites: `create_components` and FASTA data.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param component:   Component to align, or `None` for all.
    """
    model = global_view.current_model()
    
    if not all( x.site_array for x in model.sequences ):
        raise ValueError( "Refusing to make alignments because there is no site data. Did you mean to load the site data (FASTA) first?" )
    
    to_do = cli_view_utils.get_component_list( component )
    before = sum( x.alignment is not None for x in model.components )
    
    for component_ in MCMD.iterate( to_do, "Aligning", text = True ):
        algorithms.s5_alignment.create_alignments( algorithm, component_ )
    
    after = sum( x.alignment is not None for x in model.components )
    MCMD.progress( "{} components aligned. {} of {} components have an alignment ({}).".format( len( to_do ), after, len( model.components ), string_helper.as_delta( after - before ) ) )
    
    return EChanges.COMP_DATA


@command()
def create_trees( algorithm: Optional[str] = None, component: Optional[List[LegoComponent]] = None ):
    """
    Generates component trees.
    
    Requisites: `create_alignments`
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param component:   Component, or `None` for all.
    """
    model = global_view.current_model()
    
    if not all( x.alignment is not None for x in model.components ):
        raise ValueError( "Refusing to generate trees because there are no alignments. Did you mean to align the sequences first?" )
    
    to_do = cli_view_utils.get_component_list( component )
    before = sum( x.tree is not None for x in model.components )
    
    for component_ in MCMD.iterate( to_do, "Generating trees", text = True ):
        algorithms.s6_tree.create_tree( algorithm, component_ )
    
    after = sum( x.tree is not None for x in model.components )
    MCMD.progress( "{} trees generated. {} of {} components have a tree ({}).".format( len( to_do ), after, len( model.components ), string_helper.as_delta( after - before ) ) )
    
    return EChanges.COMP_DATA


@command()
def create_fusions() -> EChanges:
    """
    Makes the fusion points.
    
    Requisites: `create_trees`
    """
    model = global_view.current_model()
    
    for x in model.components:
        if x.tree is None:
            raise ValueError( "Cannot find fusion events because there is no tree data for at least one component ({}). Did you mean to generate the trees first?".format( x ) )
    
    algorithms.s7_fusion_events.create_fusions( model )
    
    n = len( model.fusion_events )
    MCMD.progress( "{} {} detected".format( n, "fusion" if n == 1 else "fusions" ) )
    
    return EChanges.MODEL_DATA


@command()
def create_splits() -> EChanges:
    """
    Creates the candidate splits.
    
    Requisites: `create_fusions`
    """
    algorithms.s8_splits.create_splits( global_view.current_model() )
    return EChanges.MODEL_DATA


@command()
def create_consensus( cutoff: float = 0.5 ) -> EChanges:
    """
    Filters the candidate splits.
    
    Requisites: `create_splits`
    
    :param cutoff:      Cutoff on consensus
    """
    algorithms.s9_consensus.create_consensus( global_view.current_model(), cutoff )
    return EChanges.MODEL_DATA


@command()
def create_subsets( super: bool = False ) -> EChanges:
    """
    Creates leaf subsets.
    
    Requisites: `create_consensus`
    
    :param super:    Keep supersets in the trees. You don't want this.
                     Turn it on to see the supersets in the final graph (your NRFG will therefore be a disjoint union of multiple possibilities!).
    """
    algorithms.s10_subsets.create_subsets( global_view.current_model(), not super )
    return EChanges.MODEL_DATA

@command()
def create_pregraphs(  ) -> EChanges:
    """
    Creates the pregraphs.
    
    Requisites: `create_subsets`
    """
    algorithms.s11_pregraphs.create_pregraphs( global_view.current_model() )
    return EChanges.MODEL_DATA

@command()
def create_subgraphs( algorithm: str = "" ) -> EChanges:
    """
    Creates the subgraphs.
    
    Requisites: `create_pregraphs`
    
    :param algorithm: Algorithm to use, see `algorithm_help`.
    """
    algorithms.s12_supertrees.create_supertrees( algorithm, global_view.current_model() )
    return EChanges.MODEL_DATA


@command()
def create_fused() -> EChanges:
    """
    Creates the NRFG (uncleaned).
    
    Requisites: `create_subgraphs`
    """
    algorithms.s13_fuse.create_fused( global_view.current_model() )
    return EChanges.MODEL_DATA


@command()
def create_cleaned() -> EChanges:
    """
    Cleans the NRFG.
    
    Requisites: `create_fused`
    """
    algorithms.s14_clean.create_cleaned( global_view.current_model() )
    return EChanges.MODEL_DATA


@command()
def create_checked() -> EChanges:
    """
    Checks the NRFG.
    
    Requisites: `create_cleaned`
    """
    algorithms.s15_checked.create_checked( global_view.current_model() )
    return EChanges.MODEL_DATA
