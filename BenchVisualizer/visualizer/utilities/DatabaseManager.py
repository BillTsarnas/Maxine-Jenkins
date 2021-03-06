from visualizer.models import Job, Specjvm, Dacapo
from django.http import Http404
from django.db import IntegrityError

class DatabaseManager:

    """
    Provides an API for the access to the DB
    """

    def clear_database(self):

        """
        Clears the contents of the database
        Warning: Does not reset auto-increment fields in tables
        :return: "ok" for successful operation, exception otherwise
        """

        Job.objects.all().delete()

        return "ok"

    def get_job(self, job_name):

        """
        Fetches a row of the table 'Jobs' from the DB in a dict.

        :param job_name: Name of the Job
        :return: Dict containing the row
        :raise: Http404 exception when job not found
        """

        try:
            stored_job = Job.objects.get(name=job_name)
        except Job.DoesNotExist:
            raise Http404("Job <" + str(job_name) + "> does not exist!")

        job ={
            'name': stored_job.name,
            'description': stored_job.description,
            'is_running': stored_job.is_running,
            'is_enabled': stored_job.is_enabled,
        }

        return job

    def get_jobs(self):

        """
        Fetches all the rows of the table 'Jobs' from the DB

        :return: a list of 'Job' dicts
        """

        job_names = Job.objects.values_list('name', flat=True)

        jobs = []

        for job_name in job_names:
            jobs.append(self.get_job(job_name))

        return jobs


    def get_benchmarks(self, stored_job, build_rev, details="default"):

        """
        Fetches the set of benchmarks (specjvm AND dacapo) of a specific build, from the DB

        :param stored_job: A Django reference to a stored Job (result of store_job())
        :param build_rev: The GIT revision of the build
        :param details: The TAG field, when build is tagged, 'default' otherwise
        :return: A dict that contains the set of benchmarks
        :raise: Http404 when build is not found
        """

        try:
            stored_dacapo = stored_job.dacapo_set.get(revision=build_rev, details=details)
            stored_specjvm = stored_job.specjvm_set.get(revision=build_rev, details=details)
        except Dacapo.DoesNotExist:
            raise Http404("Build for revision,tag: <" + str(build_rev) + "," + str(details) + "> of Job <" + stored_job.name + "> does not exist!")

        dacapo = {
            'build_no': stored_dacapo.build_no,
            'timestamp': stored_dacapo.timestamp,
            'revision': stored_dacapo.revision,
            'details': stored_dacapo.details,
            'avrora': stored_dacapo.avrora,
            'batik': stored_dacapo.batik,
            'eclipse': stored_dacapo.eclipse,
            'fop': stored_dacapo.fop,
            'h2': stored_dacapo.h2,
            'jython': stored_dacapo.jython,
            'luindex': stored_dacapo.luindex,
            'lusearch': stored_dacapo.lusearch,
            'pmd': stored_dacapo.pmd,
            'sunflow': stored_dacapo.sunflow,
            'tomcat': stored_dacapo.tomcat,
            'tradebeans': stored_dacapo.tradebeans,
            'tradesoap': stored_dacapo.tradesoap,
            'xalan': stored_dacapo.xalan
        }

        specjvm = {
            'build_no': stored_specjvm.build_no,
            'timestamp': stored_specjvm.timestamp,
            'revision': stored_specjvm.revision,
            'details': stored_specjvm.details,
            'startup': stored_specjvm.startup,
            'compiler': stored_specjvm.compiler,
            'compress': stored_specjvm.compress,
            'crypto': stored_specjvm.crypto,
            'derby': stored_specjvm.derby,
            'mpegaudio': stored_specjvm.mpegaudio,
            'scimark': stored_specjvm.scimark,
            'serial': stored_specjvm.serial,
            'spec_sunflow': stored_specjvm.sunflow,
            'xml': stored_specjvm.xml
        }

        bench = {
            'build_no': stored_dacapo.build_no,
            'dacapo': dacapo,
            'specjvm': specjvm
        }

        return bench

    def get_last_benchmarks(self, job_name):

        """
        Gets data from the last builds, for a specific Job. This is the default function called when the user
        does not specify builds to compare for the job

        :param job_name: The name of the Job
        :return: A list of build data
        """

        stored_job = Job.objects.get(name=job_name)

        '''
        The build numbers can be fetched from either the dacapo or the specjvm table (after desc sort on build_no).
        Here dacapo table is used. 
        The simplest workaround would be to take only the last_build_no from the Job and get 
        (last_build_no - 1), but this wouldn't work if build numbers are not consecutive
        '''
        recent_builds = stored_job.dacapo_set.all().order_by('-timestamp')

        if len(recent_builds) >= 2:

            bench1 = self.get_benchmarks(stored_job, recent_builds[0].revision, recent_builds[0].details)
            bench2 = self.get_benchmarks(stored_job, recent_builds[1].revision, recent_builds[1].details)
            return [bench1, bench2]

        elif len(recent_builds) == 1:

            bench1 = self.get_benchmarks(stored_job, recent_builds[0].revision)
            return [bench1]

        elif len(recent_builds) == 0:

            return []

    def get_selected_benchmarks(self, job_name, revisions, tags):

        """
        Fetches a list of benchmark data for the builds specified by revision and tag.

        :param job_name: The name of the Job
        :param revisions: A list of revision codes for all the specific builds
        :param tags: A list of TAGS for all the specific builds
        :return: A list of benchmark data for the specific builds
        """

        stored_job = Job.objects.get(name=job_name)

        benchmarks = []

        for revision, tag in zip(revisions, tags):
            benchmarks.append(self.get_benchmarks(stored_job, revision, tag))

        return benchmarks

    def store_job(self, job):

        """
        Stores a new Job (row) in the DB.

        :param job: A dict containing Job data
        :return: A reference to the newly stored job in the DB
        """

        #firstly, store the new job in the Job table
        stored_job = Job(
            name=job["name"],
            description=job["description"],
            is_running=job["is_running"],
            is_enabled=job["is_enabled"])
        stored_job.save()

        '''
        #return a "reference" to the new row in the table Job. 
        Will be used to add specjvm/dacapo results to this job
        '''
        stored_job = Job.objects.get(name=job["name"])
        return stored_job

    def store_benchmarks(self, job, bench, details="default"):

        """
        Stores a set of benchmarks of a specific build in the DB (to the tables Specjvm and Dacapo)

        :param job: The name of the Job of the build
        :param bench: A dict that contains the sets of benchmarks
        :param details: The TAG if the build is tagged, "default" otherwise
        :return: "ok" for successful operation
        """

        dacapo = bench['dacapo']
        specjvm = bench['specjvm']

        job.dacapo_set.create(
            build_no=bench['build_no'],
            timestamp=bench['timestamp'],
            revision=bench['revision'],
            details=details,
            avrora=dacapo['avrora'],
            batik=dacapo['batik'],
            eclipse=dacapo['eclipse'],
            fop=dacapo['fop'],
            h2=dacapo['h2'],
            jython=dacapo['jython'],
            luindex=dacapo['luindex'],
            lusearch=dacapo['lusearch'],
            pmd=dacapo['pmd'],
            sunflow=dacapo['sunflow'],
            tomcat=dacapo['tomcat'],
            tradebeans=dacapo['tradebeans'],
            tradesoap=dacapo['tradesoap'],
            xalan=dacapo['xalan']
        )

        job.specjvm_set.create(
            build_no=bench['build_no'],
            timestamp=bench['timestamp'],
            revision=bench['revision'],
            details=details,
            startup=specjvm['startup'],
            compiler=specjvm['compiler'],
            compress=specjvm['compress'],
            crypto=specjvm['crypto'],
            derby=specjvm['derby'],
            mpegaudio=specjvm['mpegaudio'],
            scimark=specjvm['scimark'],
            serial=specjvm['serial'],
            sunflow=specjvm['spec_sunflow'],
            xml=specjvm['xml']
        )

        return "ok"

    def update_benchmarks(self, stored_job, build_rev, bench, details="default"):
        '''
        Update the benchmarks for a stored job in the DataBase

        :param stored_build: A reference to the stored build in the DB
        :param bench: The dict with the benchmarks
        :param details: The TAG of the build
        :return: "ok" if the operation is completed, Integrity exception otherwise
        '''

        try:
            stored_dacapo = stored_job.dacapo_set.get(revision=build_rev, details=details)
            stored_specjvm = stored_job.specjvm_set.get(revision=build_rev, details=details)
        except Dacapo.DoesNotExist:
            raise Http404("Build for revision <" + str(build_rev) + "> of Job <" + stored_job.name + "> does not exist!")

        dacapo = bench['dacapo']
        specjvm = bench['specjvm']

        stored_dacapo.build_no = bench['build_no']
        stored_dacapo.timestamp = bench['timestamp']
        # revision = bench['revision']
        # details = details
        stored_dacapo.avrora = dacapo['avrora']
        stored_dacapo.batik = dacapo['batik']
        stored_dacapo.eclipse = dacapo['eclipse']
        stored_dacapo.fop = dacapo['fop']
        stored_dacapo.h2 = dacapo['h2']
        stored_dacapo.jython = dacapo['jython']
        stored_dacapo.luindex = dacapo['luindex']
        stored_dacapo.lusearch = dacapo['lusearch']
        stored_dacapo.pmd = dacapo['pmd']
        stored_dacapo.sunflow = dacapo['sunflow']
        stored_dacapo.tomcat = dacapo['tomcat']
        stored_dacapo.tradebeans = dacapo['tradebeans']
        stored_dacapo.tradesoap = dacapo['tradesoap']
        stored_dacapo.xalan = dacapo['xalan']

        stored_dacapo.save()

        stored_specjvm.build_no = bench['build_no']
        stored_specjvm.timestamp = bench['timestamp']
        # revision = bench['revision']
        # details = details
        stored_specjvm.startup = specjvm['startup']
        stored_specjvm.compiler = specjvm['compiler']
        stored_specjvm.compress = specjvm['compress']
        stored_specjvm.crypto = specjvm['crypto']
        stored_specjvm.derby = specjvm['derby']
        stored_specjvm.mpegaudio = specjvm['mpegaudio']
        stored_specjvm.scimark = specjvm['scimark']
        stored_specjvm.serial = specjvm['serial']
        stored_specjvm.sunflow = specjvm['spec_sunflow']
        stored_specjvm.xml = specjvm['xml']

        stored_specjvm.save()

        return "ok"



    def refresh_database(self, jobs):

        '''
        This function purges the old contents of the DB and inserts the new ones

        :param jobs: An array of details about each Job ('details') and its builds ('builds')
        :return: "ok" after successful operation, exception value if unsuccessful

        '''

        self.clear_database()

        try:
            for job in jobs:
                stored_job = self.store_job(job['details'])

                # for each job, store its build data
                for build in job['builds']:
                    self.store_benchmarks(stored_job, build)
        except IntegrityError as i:
            return "Integrity Error: " + str(i)

        return "ok"

    def update_database(self, jobs):

        '''
        This function updates the DB with data for new Jobs, that previously did not exist.

        :param jobs: An array of details about each Job ('details') and its builds ('builds')
        :return: "ok" after successful operation, exception value if unsuccessful
        '''
        try:
            for job in jobs:
                stored_job = self.store_job(job['details'])

                # for each job, store its build data
                for build in job['builds']:
                    self.store_benchmarks(stored_job, build)
        except IntegrityError as i:
            return "Integrity Error: " + str(i)

        return "ok"
