import random

from django.conf import settings


class PrimaryDBRouter:

    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen replica if backend node
        Else go to default DB
        """
        replicas = ['read_replica_1', 'read_replica_2']
<<<<<<< HEAD
        return random.choice(replicas)
=======
        if settings.JOBS_NODE:
            return random.choice(replicas)
        if settings.CELERY_NODE:
            return random.choice(replicas)
        return 'default'
>>>>>>> 87fcaba38 (Extract grants models into individual files (#9341))

    def db_for_write(self, model, **hints):
        """
        Writes always go to primary.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.
        """
        db_set = {'default', 'read_replica_1', 'read_replica_2'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return True  # TODO: be more stringent about this IFF we ever have a situation in which diff tables are on diff DBs

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        if db == 'default':
            return True
        return False
