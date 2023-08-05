# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# -----------------------------------------------------------------------------
# Name:         Isogeo
# Purpose:      Python minimalist SDK to use Isogeo API
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      22/12/2015
# Updated:      10/01/2016
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import locale
import logging
from math import ceil
import re
from six import string_types
from sys import platform as opersys

# 3rd party library
import requests

# modules
try:
    from . import checker
    from . import utils
except (ImportError, ValueError, SystemError):
    import checker
    import utils

# ##############################################################################
# ########## Globals ###############
# ##################################

checker = checker.IsogeoChecker()
utils = utils.IsogeoUtils()
version = "2.19.4"

# #############################################################################
# ########## Classes ###############
# ##################################

__all__ = ["Isogeo", "IsogeoChecker", "IsogeoTranslator", "IsogeoUtils"]


class Isogeo(object):
    """Abstraction class for Isogeo REST API.

    Full doc at: https://goo.gl/V3iB9R
    Swagger at: http://chantiers.hq.isogeo.fr/docs/Isogeo.Api/latest/Api.V1/
    """

    # -- ATTRIBUTES -----------------------------------------------------------
    API_URLS = {"prod": "api",
                "qa": "api.qa"
                }

    AUTH_MODES = {"group",
                  "user_private",
                  "user_public",
                  }

    SUBRESOURCES = ("_creator",
                    "conditions",
                    "contacts",
                    "coordinate-system",
                    "events",
                    "feature-attributes",
                    "keywords",
                    "layers",
                    "limitations",
                    "links",
                    "operations",
                    "serviceLayers",
                    "specifications",
                    "tags",
                    )

    FILTER_KEYS = {"action": [],
                   "catalog": [],
                   "contact:group": [],
                   "contact:isogeo": [],
                   "coordinate-system": [],
                   "format": [],
                   "has-no": [],
                   "keyword:isogeo": [],
                   "keyword:inspire-theme": [],
                   "license:group": [],
                   "license:isogeo": [],
                   "owner": [],
                   "text": [],
                   "type": []}

    FILTER_TYPES = ("dataset",
                    "raster-dataset",
                    "vector-dataset",
                    "resource",
                    "service"
                    )

    GEORELATIONS = ("contains",
                    "disjoint",
                    "equal",
                    "intersects",
                    "overlaps",
                    "within"
                    )

    THESAURI_DICT = {"isogeo": "1616597fbc4348c8b11ef9d59cf594c8",
                     "inspire-theme": "926c676c380046d7af99bcae343ac813",
                     "iso19115-topic": "926f969ee2bb470a84066625f68b96bb"
                     }

    # -- BEFORE ALL -----------------------------------------------------------

    def __init__(self, client_id, client_secret, auth_mode="group",
                 platform="prod", lang="en", proxy=None):
        r"""Isogeo API class initialization.

        Keyword arguments:
            client_id -- application identifier
            client_secret -- application secret
            platform -- switch between to production or quality assurance platform
            lang -- language asked for localized tags (INSPIRE themes).
            Could be "en" [DEFAULT] or "fr".
            proxy -- to pass through the local
            proxy. Optional. Must be a dict { 'protocol':
            'http://username:password@proxy_url:port' }.\ e.g.: {'http':
            'http://martin:p4ssW0rde@10.1.68.1:5678',\ 'https':
            'http://martin:p4ssW0rde@10.1.68.1:5678'})
        """
        super(Isogeo, self).__init__()
        self.app_id = client_id
        self.ct = client_secret

        # checking internet connection
        if checker.check_internet_connection:
            logging.info("Your're connected to the world!")
        else:
            logging.error("Internet connection doesn't work.")
            raise EnvironmentError("Internet connection issue.")

        # testing parameters
        if len(client_secret) != 64:
            logging.error("App secret length issue: it should be 64 chars.")
            raise ValueError(1, "Secret isn't good: : it must be 64 chars.")
        else:
            pass

        # auth mode
        if auth_mode not in self.AUTH_MODES:
            logging.error("Auth mode value is not good: {}".format(auth_mode))
            raise ValueError("Mode value must be one of: "
                             .format(" | ".join(self.AUTH_MODES)))
        else:
            pass

        # platform to request
        # self.platform = platform.lower()
        # if platform == "prod":
        #     self.base_url = self.API_URLS.get(platform)
        #     logging.info("Using production platform.")
        # elif platform == "qa":
        #     self.base_url = self.API_URLS.get(platform)
        #     logging.info("Using Quality Assurance platform (reduced perfs).")
        # else:
        #     logging.error("Platform must be one of: {}"
        #                   .format(" | ".join(self.API_URLS.keys())))
        #     raise ValueError(3, "Platform must be one of: {}"
        #                         .format(" | ".join(self.API_URLS.keys())))
        self.platform, self.base_url = utils.set_base_url(platform)

        # setting language
        if lang.lower() not in ("fr", "en"):
            logging.info("Isogeo API is only available in English ('en', "
                         "default) or French ('fr'). "
                         "Language has been set on English.")
            self.lang = "en"
        else:
            self.lang = lang.lower()

        # setting locale according to the language passed
        try:
            if opersys == 'win32':
                if lang.lower() == "fr":
                    locale.setlocale(locale.LC_ALL, str("fra_fra"))
                else:
                    locale.setlocale(locale.LC_ALL, str("uk_UK"))
            else:
                if lang.lower() == "fr":
                    locale.setlocale(locale.LC_ALL, str("fr_FR.utf8"))
                else:
                    locale.setlocale(locale.LC_ALL, str("en_GB.utf8"))
        except locale.Error as e:
            logging.error('Selected locale is not installed: '.format(e))

        # handling proxy parameters
        # see: http://docs.python-requests.org/en/latest/user/advanced/#proxies
        if proxy and type(proxy) is dict and 'http' in list(proxy.keys()):
            logging.info("Proxy activated")
            self.proxies = proxy
        elif proxy and type(proxy) is not dict:
            logging.info("Proxy syntax error. Must be a dict: { 'protocol': "
                         "'http://user:password@proxy_url:port' }."
                         "e.g.: {'http': 'http://martin:1234@10.1.68.1:5678',"
                         "'https': 'http://martin:p4ssW0rde@10.1.68.1:5678'}")
            return
        else:
            self.proxies = {}
            logging.info("No proxy set. Use default configuration.")
            pass

        # get API version
        logging.info("Isogeo API version: {}".format(utils.get_isogeo_version()))
        logging.info("Isogeo DB version: {}".format(utils.get_isogeo_version("db")))

    # -- API CONNECTION ------------------------------------------------------
    def connect(self, client_id=None, client_secret=None):
        """Authenticate application and get token bearer.

        Isogeo API uses oAuth 2.0 protocol (http://tools.ietf.org/html/rfc6749)
        see: https://goo.gl/V3iB9R#heading=h.ataz6wo4mxc5
        """
        # instanciated or direct call
        if not client_id and not client_secret:
            client_id = self.app_id
            client_secret = self.ct
        else:
            pass

        # Basic Authentication header in Base64 (https://en.wikipedia.org/wiki/Base64)
        # see: http://tools.ietf.org/html/rfc2617#section-2
        # using Client Credentials Grant method
        # see: http://tools.ietf.org/html/rfc6749#section-4.4
        payload = {"grant_type": "client_credentials"}
        head = {"user-agent": "isogeo-pysdk/{}".format(version)}

        # passing request to get a 24h bearer
        # see: http://tools.ietf.org/html/rfc6750#section-2
        id_url = "https://id.{}.isogeo.com/oauth/token".format(self.base_url)
        try:
            conn = requests.post(id_url,
                                 auth=(client_id, client_secret),
                                 headers=head,
                                 data=payload,
                                 proxies=self.proxies)
        except ConnectionError:
            return "No internet connection"
        except requests.exceptions.SSLError as e:
            logging.error(e)
            conn = requests.post(id_url,
                                 auth=(client_id, client_secret),
                                 data=payload,
                                 proxies=self.proxies,
                                 verify=False)

        # just a fast check
        check_params = checker.check_api_response(conn)
        if check_params == 1:
            pass
        elif type(check_params) == tuple and len(check_params) == 2:
            raise ValueError(2, check_params)

        # getting access
        axx = conn.json()

        # end of method
        return (axx.get("access_token"), axx.get("expires_in"))

    # -- API PATHS ------------------------------------------------------------

    def search(self,
               token,
               query="",
               bbox=None,
               poly=None,
               georel=None,
               order_by="_created",
               order_dir="desc",
               page_size=100,
               offset=0,
               share=None,
               specific_md=None,
               sub_resources=None,
               whole_share=True,
               check=True,
               augment=False,
               prot="https"):
        r"""Search request.

        Keyword arguments:
        token -- API bearer
        query -- search terms. It could be a simple string like 'oil' or a tag
        like 'keyword:isogeo:formations' or 'keyword:inspire-theme:landcover'.
        \nThe AND operator is applied when various tags are passed.\nEmpty by default.
        bbox -- Bounding box to limit the search. Must be a 4 list of coordinates in WGS84 (EPSG 4326).\
        \nCould be completed with the georel parameter
        poly -- Geographic criteria for the search, in WKT format.\
        \nCould be completed by the georel parameter.
        georel -- spatial operator to apply to the bbox or poly parameters.\
        \n\tAvailable values: 'contains', 'disjoint', 'equals', 'intersects' [DEFAULT],\
        'overlaps', 'within'. To get available values: 'isogeo.GEORELATIONS'.
        order_by -- to sort results. \n\tAvailable values:\n\t'_created': metadata
        creation date [DEFAULT]\n\t'_modified': metadata last update\n\t'title': metadata title\n\t'created': data
        creation date (possibly None)\n\t'modified': data last update date\n\t'relevance': relevance score.
        order_dir -- sorting direction. \n\tAvailable values:\n\t'desc':
        descending [DEFAULT]\n\t'asc': ascending
        page_size -- limits the number of results. Useful to paginate results display.
        offset -- offset
        share -- share segregation
        specific_md -- Limits the search to the specified identifiers
        sub_resources -- subresources that should be returned. Must be a list of strings.\\n
        To get available values: 'isogeo.SUBRESOURCES'
        whole_share -- option to return all results or only the page size. True by DEFAULT.
        augment -- option to improve API response by adding some values.
        prot -- https [DEFAULT] or http (useful for development and tracking requests).

        see: https://goo.gl/V3iB9R
        """
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # specific resources specific parsing
        if type(specific_md) is list and len(specific_md) > 0:
            specific_md = ",".join(specific_md)
        elif specific_md is None:
            specific_md = ""
        else:
            specific_md = ""

        # sub resources specific parsing
        if isinstance(sub_resources, string_types) and sub_resources.lower() == "all":
            sub_resources = self.SUBRESOURCES
        elif type(sub_resources) is list and len(sub_resources) > 0:
            sub_resources = ",".join(sub_resources)
        elif sub_resources is None:
            sub_resources = ""
        else:
            sub_resources = ""
            raise ValueError("Error: sub_resources argument must be a list,"
                             "'all' or empty")

        # handling request parameters
        payload = {'_id': specific_md,
                   '_include': sub_resources,
                   '_lang': self.lang,
                   '_limit': page_size,
                   '_offset': offset,
                   'box': bbox,
                   'geo': poly,
                   'rel': georel,
                   'ob': order_by,
                   'od': order_dir,
                   'q': query,
                   's': share,
                   }

        if check:
            checker.check_request_parameters(payload)
        else:
            pass

        # search request
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/{}".format(version)}
        search_url = "{}://v1.{}.isogeo.com/resources/search".format(prot,
                                                                     self.base_url)
        try:
            search_req = requests.get(search_url,
                                      headers=head,
                                      params=payload,
                                      proxies=self.proxies)
        except requests.exceptions.SSLError as e:
            logging.error(e)
            search_req = requests.get(search_url,
                                      headers=head,
                                      params=payload,
                                      proxies=self.proxies,
                                      verify=False)
        # fast response check
        checker.check_api_response(search_req)

        # serializing result into dict and storing resources in variables
        search_rez = search_req.json()
        resources_count = search_rez.get('total')  # total of metadatas shared

        # handling Isogeo API pagination
        # see: https://goo.gl/V3iB9R#heading=h.bg6le8mcd07z
        if resources_count > page_size and whole_share:
            # if API returned more than one page of results, let's get the rest!
            metadatas = []  # a recipient list
            payload["_limit"] = 100  # now it'll get pages of 100 resources
            # let's parse pages
            for idx in range(0, int(ceil(resources_count / 100)) + 1):
                payload["_offset"] = idx * 100
                search_req = requests.get(search_url,
                                          headers=head,
                                          params=payload,
                                          proxies=self.proxies)
                # storing results by addition
                metadatas.extend(search_req.json().get("results"))
            search_rez["results"] = metadatas
        else:
            pass

        # augment option
        if augment:
            self.add_tags_shares(token, search_rez.get("tags"))
            logging.debug("Results tags augmented")
        else:
            logging.debug("No augmentation")
            pass
        # end of method
        return search_rez

    def resource(self, token, id_resource, sub_resources=[], prot="https"):
        """Get complete or partial metadata about one specific resource.

        Keyword arguments:
        token -- API bearer
        id_resource -- UUID of the resource to get
        sub_resources -- subresources that should be returned. Must be a list of strings.
        To get available values: 'isogeo.SUBRESOURCES'
        prot -- https [DEFAULT] or http (useful for development and tracking requests).
        """
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # sub resources specific parsing
        if isinstance(sub_resources, string_types) and sub_resources.lower() == "all":
            sub_resources = self.SUBRESOURCES
        elif type(sub_resources) is list and len(sub_resources) > 0:
            sub_resources = ",".join(sub_resources)
        elif sub_resources is None:
            sub_resources = ""
        else:
            sub_resources = ""
            raise ValueError("Error: sub_resources argument must be a list,"
                             "'all' or empty")

        # handling request parameters
        payload = {"id": id_resource,
                   "_include": sub_resources
                   }

        # resource search
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        md_url = "{}://v1.{}.isogeo.com/resources/{}".format(prot,
                                                             self.base_url,
                                                             id_resource)
        resource_req = requests.get(md_url,
                                    headers=head,
                                    params=payload,
                                    proxies=self.proxies
                                    )
        checker.check_api_response(resource_req)

        # end of method
        return resource_req.json()

    # -- SHARES and APPLICATIONS ---------------------------------------------

    def shares(self, token, prot="https"):
        """Get information about shares which feed the application."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # passing auth parameter
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        shares_url = "{}://v1.{}.isogeo.com/shares/".format(prot,
                                                            self.base_url)
        shares_req = requests.get(shares_url,
                                  headers=head,
                                  proxies=self.proxies)

        # checking response
        checker.check_api_response(shares_req)

        # end of method
        return shares_req.json()

    def share(self, token, share_id, prot="https"):
        """Get information about a specific share and its applications."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # passing auth parameter
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        share_url = "{}://v1.{}.isogeo.com/shares/{}".format(prot,
                                                             self.base_url,
                                                             share_id)
        share_req = requests.get(share_url,
                                 headers=head,
                                 proxies=self.proxies)

        # checking response
        checker.check_api_response(share_req)

        # end of method
        return share_req.json()

    # -- LICENCES ---------------------------------------------
    def licenses(self, token, owner_id, prot="https"):
        """Get information about licenses owned by a specific workgroup."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # handling request parameters
        payload = {'gid': owner_id,
                   }

        # search request
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        licenses_url = "{}://v1.{}.isogeo.com/groups/{}/licenses"\
                       .format(prot,
                               self.base_url,
                               owner_id
                               )
        licenses_req = requests.get(licenses_url,
                                    headers=head,
                                    params=payload,
                                    proxies=self.proxies)

        # checking response
        checker.check_api_response(licenses_req)

        # end of method
        return licenses_req.json()

    def license(self, token, license_id, prot="https"):
        """Get details about a specific license."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # handling request parameters
        payload = {'lid': license_id,
                   }

        # search request
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        license_url = "{}://v1.{}.isogeo.com/licenses/{}"\
                      .format(prot,
                              self.base_url,
                              license_id
                              )
        license_req = requests.get(license_url,
                                   headers=head,
                                   params=payload,
                                   proxies=self.proxies)

        # checking response
        checker.check_api_response(license_req)

        # end of method
        return license_req.json()

    # -- KEYWORDS -----------------------------------------------------------

    def thesauri(self, token, prot="https"):
        """Get list of available thesauri."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # passing auth parameter
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        thez_url = "{}://v1.{}.isogeo.com/thesauri".format(prot,
                                                           self.base_url)
        thez_req = requests.get(thez_url,
                                headers=head,
                                proxies=self.proxies)

        # checking response
        checker.check_api_response(thez_req)

        # end of method
        return thez_req.json()

    def thesaurus(self, token, thez_id="1616597fbc4348c8b11ef9d59cf594c8", prot="https"):
        """Get a thesaurus."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # handling request parameters
        payload = {'tid': thez_id,
                   }

        # passing auth parameter
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        thez_url = "{}://v1.{}.isogeo.com/thesauri/{}".format(prot,
                                                              self.base_url,
                                                              thez_id)
        thez_req = requests.get(thez_url,
                                headers=head,
                                params=payload,
                                proxies=self.proxies)

        # checking response
        checker.check_api_response(thez_req)

        # end of method
        return thez_req.json()

    def keywords(self,
                 token,
                 specific_tag,
                 sub_resources=["count"],
                 prot="https"):
        """Search for specified keywords."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # specific tags specific parsing
        if type(specific_tag) is list and len(specific_tag) > 0:
            specific_tag = ",".join(specific_tag)
        elif specific_tag is None:
            specific_tag = ""
        else:
            specific_tag = ""

        # sub resources specific parsing
        if isinstance(sub_resources, string_types) and sub_resources.lower() == "all":
            sub_resources = self.SUBRESOURCES
        elif type(sub_resources) is list and len(sub_resources) > 0:
            sub_resources = ",".join(sub_resources)
        elif sub_resources is None:
            sub_resources = ""
        else:
            sub_resources = ""
            raise ValueError("Error: sub_resources argument must be a list,"
                             "'all' or empty")

        # handling request parameters
        payload = {'_include': sub_resources,
                   'kid': specific_tag,
                   }

        # search request
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        keywords_url = "{}://v1.{}.isogeo.com/keywords/{}"\
                       .format(prot,
                               self.base_url,
                               specific_tag)

        kwds_req = requests.get(keywords_url,
                                headers=head,
                                params=payload,
                                proxies=self.proxies)

        # checking response
        checker.check_api_response(kwds_req)

        # end of method
        return kwds_req.json()

    def keywords_thesaurus(self,
                           token,
                           thez_id,
                           query="",
                           offset=0,
                           order_by="text",
                           order_dir="desc",
                           page_size=20,
                           specific_md=None,
                           specific_tag=None,
                           sub_resources=["count"],
                           prot="https"):
        """Search for keywords within a specific thesaurus."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # specific resources specific parsing
        if type(specific_md) is list and len(specific_md) > 0:
            specific_md = ",".join(specific_md)
        elif specific_md is None:
            specific_md = ""
        else:
            specific_md = ""

        # specific tags specific parsing
        if type(specific_tag) is list and len(specific_tag) > 0:
            specific_tag = ",".join(specific_tag)
        elif specific_tag is None:
            specific_tag = ""
        else:
            specific_tag = ""

        # sub resources specific parsing
        if isinstance(sub_resources, string_types) and sub_resources.lower() == "all":
            sub_resources = self.SUBRESOURCES
        elif type(sub_resources) is list and len(sub_resources) > 0:
            sub_resources = ",".join(sub_resources)
        elif sub_resources is None:
            sub_resources = ""
        else:
            sub_resources = ""
            raise ValueError("Error: sub_resources argument must be a list,"
                             "'all' or empty")

        # handling request parameters
        payload = {'_id': specific_md,
                   '_include': sub_resources,
                   '_limit': page_size,
                   '_offset': offset,
                   '_tag': specific_tag,
                   'tid': thez_id,
                   'ob': order_by,
                   'od': order_dir,
                   'q': query,
                   }

        # search request
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        keywords_url = "{}://v1.{}.isogeo.com/thesauri/{}/keywords/search"\
                       .format(prot,
                               self.base_url,
                               thez_id)

        kwds_req = requests.get(keywords_url,
                                headers=head,
                                params=payload,
                                proxies=self.proxies)

        # checking response
        checker.check_api_response(kwds_req)

        # end of method
        return kwds_req.json()

    def keywords_workgroup(self,
                           token,
                           owner_id,
                           query="",
                           thez_id="1616597fbc4348c8b11ef9d59cf594c8",
                           offset=0,
                           order_by="text",
                           order_dir="desc",
                           page_size=20,
                           specific_md=None,
                           specific_tag=None,
                           sub_resources=["count"],
                           prot="https"):
        """Search for keywords within a specific workgroup."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # specific resources specific parsing
        if type(specific_md) is list and len(specific_md) > 0:
            specific_md = ",".join(specific_md)
        elif specific_md is None:
            specific_md = ""
        else:
            specific_md = ""

        # specific tags specific parsing
        if type(specific_tag) is list and len(specific_tag) > 0:
            specific_tag = ",".join(specific_tag)
        elif specific_tag is None:
            specific_tag = ""
        else:
            specific_tag = ""

        # sub resources specific parsing
        if isinstance(sub_resources, string_types) and sub_resources.lower() == "all":
            sub_resources = self.SUBRESOURCES
        elif type(sub_resources) is list and len(sub_resources) > 0:
            sub_resources = ",".join(sub_resources)
        elif sub_resources is None:
            sub_resources = ""
        else:
            sub_resources = ""
            raise ValueError("Error: sub_resources argument must be a list,"
                             "'all' or empty")

        # handling request parameters
        payload = {'_id': specific_md,
                   '_include': sub_resources,
                   '_limit': page_size,
                   '_offset': offset,
                   '_tag': specific_tag,
                   'gid': owner_id,
                   'th': thez_id,
                   'ob': order_by,
                   'od': order_dir,
                   'q': query,
                   }

        # search request
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        keywords_url = "{}://v1.{}.isogeo.com/groups/{}/keywords/search"\
                       .format(prot,
                               self.base_url,
                               owner_id)

        kwds_req = requests.get(keywords_url,
                                headers=head,
                                params=payload,
                                proxies=self.proxies)

        # checking response
        checker.check_api_response(kwds_req)

        # end of method
        return kwds_req.json()

    # -- DOWNLOADS -----------------------------------------------------------

    def dl_hosted(self, token, id_resource, resource_link, proxy_url=None, prot="https"):
        """Download hosted resource."""
        # check resource link compliance
        if type(resource_link) is dict and resource_link.get("type") == "hosted":
            id_link = resource_link.get("_id")
            pass
        else:
            return "Error: resource link passed is not valid or not a hosted one."

        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # handling request parameters
        payload = {'proxyUrl': proxy_url}

        # resource search
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        hosted_url = "{}://v1.{}.isogeo.com/resources/{}/links/{}.bin"\
                     .format(prot,
                             self.base_url,
                             id_resource,
                             id_link)

        hosted_req = requests.get(hosted_url,
                                  headers=head,
                                  stream=True,
                                  params=payload,
                                  proxies=self.proxies
                                  )

        # get filename from header
        content_disposition = hosted_req.headers.get("Content-Disposition")
        filename = re.findall("filename=(.+)", content_disposition)

        # well-formed size
        in_size = resource_link.get("size")
        for size_cat in ('octets', 'Ko', 'Mo', 'Go'):
            if in_size < 1024.0:
                out_size = "%3.1f %s" % (in_size, size_cat)
            in_size /= 1024.0

        out_size = "%3.1f %s" % (in_size, " To")

        # end of method
        return (hosted_req, filename[0], out_size)

    def xml19139(self, token, id_resource, proxy_url=None, prot="https"):
        """Get resource exported into XML ISO 19139."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id, self.ct))

        # handling request parameters
        payload = {'proxyUrl': proxy_url,
                   'id': id_resource,
                   }

        # resource search
        head = {"Authorization": "Bearer " + token[0],
                "user-agent": "isogeo-pysdk/2.19.451"}
        md_url = "{}://v1.{}.isogeo.com/resources/{}.xml".format(prot,
                                                                 self.base_url,
                                                                 id_resource)
        xml_req = requests.get(md_url,
                               headers=head,
                               stream=True,
                               params=payload,
                               proxies=self.proxies
                               )

        # end of method
        return xml_req

    # -- UTILITIES -----------------------------------------------------------

    def add_tags_shares(self, token, results_tags=dict()):
        """Add shares list to the tags attributes in search results."""
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id,
                                                                  self.ct))
        # check if shares_id have already been retrieved or not
        if not hasattr(self, "shares_id"):
            shares = self.shares(token)
            self.shares_id = {"share:{}".format(i.get("_id")): i.get("name")
                              for i in shares}
        else:
            pass
        results_tags.update(self.shares_id)
        return

    def get_app_properties(self, token, prot="https"):
        """Get information about the application declared on Isogeo."""
        mng_base_url = "https://manage.isogeo.com/applications/"
        # checking bearer validity
        token = checker.check_bearer_validity(token, self.connect(self.app_id,
                                                                  self.ct))
        # check if shares_id have already been retrieved or not
        if not hasattr(self, "shares_id"):
            first_share = self.shares(token)[0].get("applications")[0]
            app = {"admin_url": mng_base_url + first_share.get("_id"),
                   "creation_date": first_share.get("_created"),
                   "last_update": first_share.get("_modified"),
                   "name": first_share.get("name"),
                   "type": first_share.get("type"),
                   "url": first_share.get("url")
                   }
            self.app_properties = app
        else:
            pass

    # def get_csw_record_by_id(self, id_resource=str):
    #     """
    #         TO DOC
    #     """
    #     srv_link_xml = "http://services.api.isogeo.com/ows/s/"\
    #                            "{1}/{2}?"\
    #                            "service=CSW&version=2.0.2&request=GetRecordById"\
    #                            "&id=urn:isogeo:metadata:uuid:{0}&"\
    #                            "elementsetname=full&outputSchema="\
    #                            "http://www.isotc211.org/2005/gmd"\
    #                            .format(md_uuid_formatted,
    #                                    csw_share_id,
    #                                    csw_share_token)
    #     pass


# ##############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """ standalone execution """
    # ------------ Specific imports ----------------
    from os import environ

    # ------------ Log & debug ----------------
    logger = logging.getLogger()
    logging.captureWarnings(True)
    logger.setLevel(logging.INFO)

    # ------------ Settings from ini file ----------------
    share_id = environ.get('ISOGEO_API_DEV_ID')
    share_token = environ.get('ISOGEO_API_DEV_SECRET')

    if not share_id or not share_token:
        logging.critical("No API credentials set as env variables.")
        exit()
    else:
        pass

    # ------------ Real start ----------------
    # instanciating the class
    isogeo = Isogeo(client_id=share_id,
                    client_secret=share_token,
                    mode="group",
                    lang="fr",
                    # platform="qa"
                    )

    # getting a token
    token = isogeo.connect()

    # let's search for metadatas!
    search = isogeo.search(token,
                           # sub_resources='all',
                           # sub_resources=["conditions", "contacts"],
                           # sub_resources=isogeo.SUBRESOURCES,
                           query="keyword:isogeo:2015\
                                  type:dataset",
                           prot='https')
