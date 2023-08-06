from datetime import date
from munch import Munch
from munch import munchify
from twisted.internet import defer
from txproductpages.exceptions import TaskNotFoundException


class Release(Munch):

    @defer.inlineCallbacks
    def schedule_tasks(self):
        """
        Get all the tasks for a release.

        :param release_id: int, release id number.
        :returns: deferred that when fired returns a list of Munch (dict-like)
                  objects representing all tasks.
        """
        url = 'api/v6/releases/%d/schedule-tasks' % self.id
        tasks = yield self.connection._get(url)
        defer.returnValue(munchify(tasks))

    @defer.inlineCallbacks
    def task_date(self, task_re):
        """ Get a datetime.date object for the last task that matches a regex.

        :param task_re: regex, eg re.compile('Development Freeze').
                        See txproductpages.milestones for some useful regex
                        constants to pass in here.
        :returns: deferred that when fired returns a datetime.date object
        :raises: TaskNotFoundException if no tasks matched.
        """
        tasks = yield self.schedule_tasks()
        task_date = None
        for task in tasks:
            if task_re.match(task['name']):
                (y, m, d) = task['ac_date_finish'].split('-')
                task_date = date(int(y), int(m), int(d))
        if task_date:
            defer.returnValue(task_date)
        raise TaskNotFoundException()
