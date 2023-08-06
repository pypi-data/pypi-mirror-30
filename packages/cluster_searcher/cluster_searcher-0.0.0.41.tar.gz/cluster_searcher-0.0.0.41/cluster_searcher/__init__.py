__version__ = "0.0.0.41"


def __setup():
    from intermake import MENV
    
    MENV.configure( name = "cluster_searcher",
                    version = __version__ )


__setup()

from cluster_searcher import commands
