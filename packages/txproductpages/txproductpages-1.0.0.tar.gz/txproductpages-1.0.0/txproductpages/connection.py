import posixpath
import treq
from munch import munchify
from datetime import date
from twisted.internet import defer
from txproductpages.release import Release
from txproductpages.exceptions import ProductPagesException
from txproductpages.exceptions import ReleaseNotFoundException


PROD = 'https://pp.engineering.redhat.com/pp-admin/'
PROD_HUMAN = 'https://pp.engineering.redhat.com/pp/'


class Connection(object):

    def __init__(self, url=PROD, human=PROD_HUMAN):
        """
        Initialize a connection to Product Pages.

        :param url: The API URL base, "https://...". Defaults to production
                    environment.
        :param human: The human-friendly UI URL base. Defaults to production
                      environment.
        """
        self.url = url
        self.human = human

    @defer.inlineCallbacks
    def upcoming_releases(self, product):
        """
        Get upcoming releases for this product.

        Specifically we search for releases with a GA date greater-than or
        equal to today's date.

        :param product: str, eg. "ceph"
        :returns: deferred that when fired returns a list of Munch (dict-like)
                  objects representing all releases, sorted by shortname.
        """
        url = 'api/v6/releases/'
        url = url + '?product__shortname=' + product
        url = url + '&ga_date__gte=' + date.today().strftime('%Y-%m-%d')
        releases = yield self._get(url)
        result = munchify(sorted(releases, key=lambda x: x['shortname']))
        defer.returnValue(result)

    @defer.inlineCallbacks
    def newest_release(self, product):
        """
        Get the shortname of the newest upcoming release for a product.

        :param product: str, eg. "ceph"
        :returns: deferred that when fired returns the shortname of the newest
                  release.
        """
        releases = yield self.upcoming_releases()
        if not releases:
            raise ProductPagesException('no upcoming releases')
        defer.returnValue(releases[0].shortname)

    @defer.inlineCallbacks
    def release(self, shortname):
        """
        Get a specific release by its shortname.

        :param shortname: str, eg. "ceph-3-0"
        :returns: deferred that when fired returns a Release (Munch, dict-like)
                  object representing this release.
        :raises: ReleaseNotFoundException if this release does not exist.
        """
        url = 'api/v6/releases/?shortname=%s' % shortname
        releases = yield self._get(url)
        # Note, even if this shortname does not exist, _get() will not errback
        # for this url. It simply returns an empty list. So check that here:
        if not releases:
            raise ReleaseNotFoundException('no release %s' % shortname)
        release = Release.fromDict(releases[0])
        release.connection = self
        defer.returnValue(release)

    def schedule_url(self, release):
        """
        Return a human-friendly URL for this release.

        :param release: str, release shortname eg. "ceph-3-0"
        :returns: str, URL
        """
        product, _ = release.split('-', 1)
        url = 'product/%s/release/%s/schedule/tasks' % (product, release)
        return posixpath.join(self.human, url)

    @defer.inlineCallbacks
    def _get(self, url, headers={}):
        """ Get a JSON API endpoint and return the parsed data.

        :param url: str, *relative* URL (relative to pp-admin/ api endpoint)
        :param headers: dict (optional)
        :returns: deferred that when fired returns the parsed data from JSON
                  or errbacks with ProductPagesException
        """
        # print('getting %s' % url)
        headers = headers.copy()
        headers['Accept'] = 'application/json'
        url = posixpath.join(self.url, url)
        try:
            response = yield treq.get(url, headers=headers, timeout=5)
            if response.code != 200:
                err = '%s returned %s' % (url, response.code)
                raise ProductPagesException(err)
            else:
                content = yield treq.json_content(response)
                defer.returnValue(content)
        except Exception as e:
            # For example, if treq.get() timed out, or if treq.json_content()
            # could not parse the JSON, etc.
            # TODO: better handling here for the specific errors?
            # I suspect it's not good to catch Exception with inlineCallbacks
            raise ProductPagesException('treq error: %s' % e.message)
