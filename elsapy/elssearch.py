"""The search module of elsapy.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

from . import log_util

logger = log_util.get_logger(__name__)


class ElsSearch:
    """Represents a search to one of the search indexes accessible
         through api.elsevier.com. Returns True if successful; else, False."""

    # static variables
    __search_path = u'content/search/'

    def __init__(self, query, page):
        """Initializes a search object with a query and target page."""
        self._query = query
        self._page = page
        self._path = self.__search_path + page

        self._total_num_results = 0
        self._results = None

    # properties
    @property
    def query(self):
        """Gets the search query"""
        return self._query

    @query.setter
    def query(self, query):
        """Sets the search query"""
        self._query = query

    @property
    def index(self):
        """Gets the label of the index targeted by the search"""
        return self._page

    @index.setter
    def index(self, index):
        self._page = index
        """Sets the label of the index targeted by the search"""

    @property
    def results(self):
        """Gets the results for the search"""
        return self._results

    @property
    def num_results(self):
        """Gets the number of results for this query that are stored in the
            search object. This number might be smaller than the number of
            results that exist in the index for the query."""
        return len(self._results)

    @property
    def total_num_results(self):
        """Gets the total number of results that exist in the index for
            this query. This number might be larger than can be retrieved
            and stored in a single ElsSearch object (i.e. 5,000)."""
        return self._total_num_results

    def has_all_results(self):
        """Returns true if the search object has retrieved all results for the
            query from the index (i.e. num_res equals tot_num_res)."""
        return self.num_results is self.total_num_results

    @property
    def uri(self):
        """Gets the request uri for the search"""
        return self._path

    def execute(self, els_client = None, get_all = False):
        """Executes the search. If get_all = False (default), this retrieves
            the default number of results specified for the API. If
            get_all = True, multiple API calls will be made to iteratively get 
            all results for the search, up to a maximum of 5,000."""
        ## TODO: add exception handling

        api_response = els_client.exec_request_with_params(self._path, {u"query": self._query})

        total_num_results = int(api_response['search-results']['opensearch:totalResults'])
        results = api_response['search-results']['entry']
        num_results = len(results)

        next_url = None
        if get_all is True:
            while (num_results < total_num_results) and (num_results < 5000):
                for entry in api_response['search-results']['link']:
                    if entry['@ref'] == 'next':
                        next_url = entry['@href']

                api_response = els_client.exec_request(next_url)
                results += api_response['search-results']['entry']
                num_results = len(results)

        self._total_num_results = total_num_results
        self._results = results
