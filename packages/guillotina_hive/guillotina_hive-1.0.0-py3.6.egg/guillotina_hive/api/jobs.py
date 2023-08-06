from guillotina import configure
from guillotina.api.service import TraversableService
from guillotina.component import get_utility
from guillotina.interfaces import IApplication
from guillotina_hive.interfaces import IHiveClientUtility


class BaseWorkerService(TraversableService):
    job_id = None
    execution_id = None

    async def publish_traverse(self, traverse):
        if len(traverse) > 2:
            raise KeyError('/'.join(traverse))
        if len(traverse) > 0:
            self.job_id = traverse[0]
        if len(traverse) > 1:
            self.execution_id = traverse[1]
        return self


# Show jobs that are running
@configure.service(context=IApplication, name='@hive-jobs', method='GET',
                   permission='guillotina_hive.Manage')
class Workers(BaseWorkerService):

    async def __call__(self):

        hive = get_utility(IHiveClientUtility)
        if self.job_id is None:
            jobs = await hive.cm.list_jobs(hive.ns)
            return jobs
        elif self.job_id is not None and self.execution_id is None:
            job = await hive.cm.get_job(hive.ns, self.job_id)
            executions = await hive.cm.list_job_executions(
                hive.ns, self.job_id)
            return job, executions
        elif self.job_id is not None and self.execution_id is not None:
            job = await hive.cm.get_job(hive.ns, self.job_id)
            executions = await hive.cm.list_job_executions(
                hive.ns, self.job_id)
            return executions[self.execution_id]


# See log of a job that is running
@configure.service(context=IApplication, name='@hive-jobs', method='HEAD',
                   permission='guillotina_hive.Manage')
class Logs(BaseWorkerService):

    async def __call__(self):

        hive = get_utility(IHiveClientUtility)
        if self.job_id is not None and self.execution_id is not None:
            log = await hive.cm.get_execution_log(
                hive.ns, self.job_id, self.execution_id)
            return log


# Stop a job that is running
@configure.service(context=IApplication, name='@hive-jobs', method='DELETE',
                   permission='guillotina_hive.Manage')
class DeleteJob(BaseWorkerService):

    async def __call__(self):

        hive = get_utility(IHiveClientUtility)

        if self.job_id is None:
            await hive.cm.delete_namespace(hive.ns)
            await hive.cm.create_namespace(hive.ns)
        elif self.job_id is not None and self.execution_id is None:
            await hive.cm.delete_job(hive.ns, self.job_id)
        if self.job_id is not None and self.execution_id is not None:
            await hive.cm.delete_execution(
                hive.ns, self.job_id, self.execution_id)
