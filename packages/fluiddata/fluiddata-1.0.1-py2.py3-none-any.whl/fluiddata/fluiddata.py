"""
FluidDATA API
"""

from __future__ import print_function

import datetime
import requests

HOST = "https://api.fluiddata.com"

class Fluid(object):
    """
    Python to FluidDATA REST endpoints.

        >>> fluid = Fluid(TOKEN)
        >>> result = fluid.query(query='Fluid Data')

    """

    def __init__(self, token):
        """
        :arg token: FluidDATA API Token.  See
            https://accounts.bitplatter.com/home/security to get your token
        """

        self.token = token
        self.headers = {
            'Authorization': 'Token %s' % self.token
        }


    def query(
            self,
            query=None,
            date_min=None,
            date_max=None,
            collection_id=None,
            page=0):
        """
        Perform a query against the FluidDATA database and return up to 10 matches

        :quota: Each call will debit 1 search credit against your quota

        :arg query: The search query or phrase to search for.
        :arg date_min: Datetime object specifying minimum search date range
        :arg date_max: Datetime object specifying maximum search date range
        :arg collection_id: The Fluid collection id or list of collection ids
            to search within
        :arg page:  Return given page of results.  For example, page 3 will
            return results 40-49

        :Example:

        >>> # Query with no collection specified
        >>> fluid.query('porcupine')
        {
            "status": <True/False>, # Response status
            "collections": None,    # Will be none since collection was not specified
            "matches": [{
                "id": <int>,        # FluidDATA audio id
                "metadata": {       # Various metadata associated with audio file
                    "album": <string>,
                    "artist": <string>,
                    "comment": <string>,
                    "duration": <float>, # Duration in seconds
                    "genre": <string>,
                    "title": <string>
                },
                "rss_item": {       # RSS Item data associated with audio result
                    "author": <string>
                    "collection_id": <int>, # FluidDATA collection id
                    "description": <string>,
                    "image_url": <string>,
                    "link": <string>, # URL from where audio was downloaded
                    "pubdate": "2017-04-05 22:00:00",
                    "subtitle": <string>,
                    "title": <string>,
                },
                "snippets": [       # Snippets of the transcript that matches query
                    "elephant right or lion right and you don't think about <b> porcupine </b> it's not something you think about too",
                    "something you think about too often that you know about <b> porcupines </b> you've heard of them you've seen them"
                ],
                "timestamps": [     # Time in seconds where match occurs in audio file
                    1887.7,
                    1890.82
                ]
            },
            ... # Up to 10 matches listed in array
            ],
            "nmatches": <int>, # Number of matches for the query
            "page": <int>, # Page requested
            "query": "porcupine"
        }

        :Example:

        >>> # Query with collection specified
        >>> fluid.query('porcupine', collection_id=410313122)
        {
            "status": <True/False>,     # Response status
            "collections": [{
                'author': <string>,
                'description': <string>,
                'id': <int>,            # FluidDATA collection id
                'image_url': <string>,
                'language': 'en-us',
                'subtitle': <string>,
                'title': <string>,
                'url': <string>,        # URL of RSS feed
            }],
            "matches": [
                # Identical to query with no collection specified, see example above
            ],
            "nmatches": <int>, # Number of matches for the query
            "query": "porcupine"
        }

        :Example:

        >>> # Query multiple collections
        >>> fluid.query('porcupine', collection_id=[410313122, 9853])

        """

        payload = {'page': page}

        if query is not None:
            payload['term'] = query

        if date_min is not None:
            payload['date_min'] = datetime.datetime.strftime(date_min, '%Y-%m-%d')

        if date_max is not None:
            payload['date_max'] = datetime.datetime.strftime(date_max, '%Y-%m-%d')

        if collection_id is not None:
            if isinstance(collection_id, list):
                payload['collection_id'] = \
                    ','.join([str(x) for x in collection_id])
            else:
                payload['collection_id'] = collection_id

        response = requests.get(
            '%s/api/v1/search' % HOST,
            params=payload,
            headers=self.headers)

        return response.json()


    def search_collection(self, query, page=0):
        """
        Searches for a collection by title or author and returns up to 10 resuts

        :quota: Does not affect quota

        FluidDATA uniquely identifies RSS Channels and other audio collections
        with a unique collection id.  You can use the collection_id parameter
        in the Fluid.query method to limit a transcript search to audio files
        in a given collection.

        This function is useful for searching for a FluidDATA channel if you
        know the RSS channel name or RSS channel author.  Once you have the
        FluidDATA collection id you can use the FluidDATA.query function to
        search for audio within that specific collection.

        :arg query: Title or author to search for

        >>> fluid.search_collection("church")
        {
            "matches": [
                {
                    "author": "Hope Church",
                    "description": "Sunday messages from Hope Church | Snohomish, WA ~ Go to hopefoursquare.com for more information. Or join us 9 or 11am Sundays!",
                    "id": 410357976,
                    "image_url": "http://static.libsyn.com/p/assets/3/c/e/2/3ce2e381efce130a/hope_icon.png",
                    "language": "en",
                    "subtitle": "Inviting people to life | Activating life in you",
                    "title": "Hope Church",
                    "url": "http://hfc.libsyn.com/rss"
                },
                ...
            ],
            "nmatches": 95,
            "page": 0,
            "query": "church",
            "status": True
        }


        """

        payload = {'term': query, 'page': page}

        response = requests.get(
            '%s/api/v1/search_collection' % HOST,
            params=payload,
            headers=self.headers)

        return response.json()



    def feed_to_collection(self, feed_url):
        """
        Get a Fluid collection for a given url

        :quota: Does not affect quota

        FluidDATA uniquely identifies RSS Channels and other audio collections
        with a unique collection id.  You can use the collection_id parameter
        in the Fluid.query method to limit a transcript search to audio files
        in a given collection.

        This function is useful for converting an RSS Channel to a FluidDATA
        collection to determine the FluidDATA collection_id used in the
        Fluid.query method.

        :arg feed_url: The rss feed url

        :Example:

        >>> fluid.feed_to_collection_id('http://feeds.priorityonepodcast.com')
        {
            "result": {
                "author": "Priority One: A Roddenberry Star Trek Podcast",
                "description": "A Roddenberry Star Trek Podcast providing a weekly report on all things Star Trek - Films/TV, Games, and more!",
                "id": 197277703,
                "image_url": "http://static.libsyn.com/p/assets/a/c/b/5/acb5fce5ba951cd4/p1logo1400x.jpg',
                "language": "en",
                "subtitle": "A Roddenberry Star Trek Podcast",
                "title": "Priority One: A Roddenberry Star Trek Podcast",
                "url": "http://feeds.priorityonepodcast.com"
            },
            "status": True,
        }
        """

        payload = {'feed_url': feed_url}

        response = requests.get(
            '%s/api/v1/feed_to_collection' % HOST,
            params=payload,
            headers=self.headers)

        return response.json()


    def subscription_info(self):
        """
        Get information about your FluidDATA subscription

        :quota: Does not affect quota

        :Example:

        >>> fluid.subscrioption_info()
        {
            u'result': {
                u'canceled': False,
                u'fluid_search': 100,           # Number of total searches allowed by the current subscription
                u'fluid_search_remaining': 76,  # Number of searches remaining for the billing period
                u'period_end': u'2018-03-13T04:51:10Z',# Date that plan resets
                u'plan': u'fluid-free-monthly', # Plan name
                u'price': u'0.00',              # Plan monthly price
                u'status': u'active',
                u'stripe_id': u'fluid-free-monthly'},
            "status": True
        }

        """

        response = requests.get(
            '%s/subscriptions/info' % HOST,
            headers=self.headers)

        return response.json()
