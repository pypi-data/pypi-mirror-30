from distutils.core import setup

setup( name = "cluster_searcher",
       url="https://bitbucket.org/mjr129/cluster_searcher",
       version = "0.0.0.39",
       description = "Searches a specific file.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = [ "cluster_searcher" ],
       entry_points= { "console_scripts": [ "cluster_searcher = cluster_searcher.__main__:main" ] },
       python_requires = ">=3.6",
       install_requires = ["colorama", 
                           "intermake",
                           "mhelper" ]
       )
