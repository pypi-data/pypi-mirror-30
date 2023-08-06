class Job(object):
    IDLE = u'idle'
    LOCKED = u'locked'
    CANCELLED = u'cancelled'
    COMPLETED = u'completed'

    def __init__(self, id_, reqs, args, version, **_3to2kwargs):
        if 'worker_exception' in _3to2kwargs: worker_exception = _3to2kwargs['worker_exception']; del _3to2kwargs['worker_exception']
        else: worker_exception = None
        if 'worker_heartbeat' in _3to2kwargs: worker_heartbeat = _3to2kwargs['worker_heartbeat']; del _3to2kwargs['worker_heartbeat']
        else: worker_heartbeat = None
        if 'worker_id' in _3to2kwargs: worker_id = _3to2kwargs['worker_id']; del _3to2kwargs['worker_id']
        else: worker_id = None
        if 'run_at' in _3to2kwargs: run_at = _3to2kwargs['run_at']; del _3to2kwargs['run_at']
        else: run_at = None
        if 'completed_at' in _3to2kwargs: completed_at = _3to2kwargs['completed_at']; del _3to2kwargs['completed_at']
        else: completed_at = None
        if 'locked_at' in _3to2kwargs: locked_at = _3to2kwargs['locked_at']; del _3to2kwargs['locked_at']
        else: locked_at = None
        if 'created_at' in _3to2kwargs: created_at = _3to2kwargs['created_at']; del _3to2kwargs['created_at']
        else: created_at = None
        if 'status' in _3to2kwargs: status = _3to2kwargs['status']; del _3to2kwargs['status']
        else: status = None
        self.id = id_
        self.reqs = reqs
        self.args = args
        self.version = version
        self.status = status or Job.IDLE
        self.created_at = created_at
        self.locked_at = locked_at
        self.completed_at = completed_at
        self.run_at = run_at
        self.worker_id = worker_id
        self.worker_heartbeat = worker_heartbeat
        self.worker_exception = worker_exception

    @property
    def failed(self):
        return self.worker_exception is not None


class RetriableError(Exception):
    pass


class ConcurrencyError(Exception):
    pass


class IJobController(object):
    def get_job(self, job_id):
        pass

    def create_job(self, job_id, **_3to2kwargs):
        if 'run_at' in _3to2kwargs: run_at = _3to2kwargs['run_at']; del _3to2kwargs['run_at']
        else: run_at = None
        if 'args' in _3to2kwargs: args = _3to2kwargs['args']; del _3to2kwargs['args']
        else: args = None
        if 'reqs' in _3to2kwargs: reqs = _3to2kwargs['reqs']; del _3to2kwargs['reqs']
        else: reqs = None
        pass

    def cancel_job(self, job_id, version):
        pass

    def delete_job(self, job_id, version):
        pass


class IWorkerController(object):
    def acquire_job(self, resources, worker_id):
        pass

    def heartbeat_job(self, job_id, version):
        pass

    def finalize_job(self, job_id, version, worker_exception=None):
        pass

    def requeue_job(self, job_id, version, run_at=None):
        pass
