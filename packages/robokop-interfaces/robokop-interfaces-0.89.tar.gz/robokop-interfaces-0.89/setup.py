from distutils.core import setup
#from pip.req import parse_requirements
def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

install_reqs = parse_requirements("greent/requirements.txt") #, session="i")
requirements = [str(r) for r in install_reqs]
setup(
    name = 'robokop-interfaces',
    packages = [ 'greent' ], # this must be the same as the name above
    package_data={ 'greent' : [
        'greent.conf',
        'greent-dev.conf',
        'greent-compose.conf',
        'rosetta.yml',
        'requirements.txt',
        'api/*',
        'conf/*',
        'jsonld/*',
        'ontologies/*',
        'query/*.sparql',
        'registry/layers/biolink/jsonld/*',
        'services/*.py',
        'services/*.txt',
        'synonymizers/*',
        'test/*'
    ]},
    version = '0.89',
    description = 'Translator API',
    author = 'Steve Cox',
    author_email = 'scox@renci.org',
    install_requires = requirements,
    include_package_data=True,
    url = 'http://github.com/NCATS-Gamma/robokop-interfaces.git',
    download_url = 'http://github.com/NCATS-Gamma/robokop-interfaces/archive/0.1.tar.gz',
    keywords = [ 'biomedical', 'environmental', 'exposure', 'clinical' ],
    classifiers = [ ],
)
