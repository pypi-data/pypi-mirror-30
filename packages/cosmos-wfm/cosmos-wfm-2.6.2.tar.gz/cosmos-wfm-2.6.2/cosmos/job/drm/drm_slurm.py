import datetime
import os
import re
import subprocess as sp
import time
from pprint import pformat

from more_itertools import grouper

from cosmos import TaskStatus
from cosmos.job.drm.DRM_Base import DRM
from cosmos.job.drm.util import exit_process_group, convert_size_to_kb, div

FAILED_STATES = ['BOOT_FAIL', 'CANCELLED', 'FAILED', 'NODE_FAIL', 'PREEMPTED', 'REVOKED', 'TIMEOUT']
PENDING_STATES = ['PENDING', 'CONFIGURING', 'COMPLETING', 'RUNNING', 'RESIZING', 'SUSPENDED']
COMPLETED_STATES = ['COMPLETED', ]


def parse_slurm_time(s, default=0):
    if s.strip() == '':
        return default

    p = s.split('-')
    if len(p) == 2:
        days = p[0]
        time = p[1]
    else:
        days = 0
        time = p[0]
    hours, mins, secs = time.split(':')
    return int(days) * 24 * 60 * 60 + int(hours) * 60 * 60 + int(mins) * 60 + int(secs)


def parse_slurm_time2(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


class DRM_SLURM(DRM):
    name = 'slurm'
    poll_interval = 5

    def submit_job(self, task):
        for p in [task.output_stdout_path, task.output_stderr_path]:
            if os.path.exists(p):
                os.unlink(p)

        ns = ' ' + task.drm_native_specification if task.drm_native_specification else ''
        sub = "sbatch -o {stdout} -e {stderr} {ns} {cmd_str}".format(
            stdout=task.output_stdout_path,
            stderr=task.output_stderr_path,
            ns=ns,
            cmd_str=task.output_command_script_path)

        try:
            out = sp.check_output(sub, env=os.environ, preexec_fn=exit_process_group, shell=True).decode()
            task.drm_jobID = unicode(re.search(r'job (\d+)', out).group(1))
        except sp.CalledProcessError as cpe:
            task.log.error('%s submission to %s failed with error %s: %s' %
                           (task, task.drm, cpe.returncode, cpe.output.decode().strip()))
            task.status = TaskStatus.failed
        except ValueError:
            task.log.error('%s submission to %s returned unexpected text: %s' % (task, task.drm, out))
            task.status = TaskStatus.failed
        else:
            task.status = TaskStatus.submitted

    def filter_is_done(self, tasks):
        """
        Yield a dictionary of Slurm job metadata for each task that has completed.
        """
        if tasks:
            job_infos = do_sacct([t.drm_jobID for t in tasks], tasks[0].workflow.log)

            for task in tasks:
                if task.drm_jobID in job_infos:
                    job_info = job_infos[task.drm_jobID]
                    if job_info['State'] in FAILED_STATES + COMPLETED_STATES:
                        job_info = parse_sacct(job_infos[task.drm_jobID],
                                           tasks[0].workflow.log)  # self._get_task_return_data(task)

                        yield task, job_info
                    else:
                        assert job_info['State'] in PENDING_STATES,job_info['State']

    def drm_statuses(self, tasks, log_errors=True):
        """
        :param tasks: tasks that have been submitted to the job manager
        :returns: (dict) task.drm_jobID -> drm_status
        """
        if tasks:
            job_infos = do_sacct([t.drm_jobID for t in tasks],
                                 tasks[0].workflow.log if log_errors else None,

                                 )

            def f(task):
                return job_infos.get(task.drm_jobID, dict()).get('STATE', 'UNK_JOB_STATE')

            return {task.drm_jobID: f(task) for task in tasks}
        else:
            return {}

    def kill(self, task):
        """Terminate a task."""
        raise NotImplementedError

    def kill_tasks(self, tasks):
        for group in grouper(50, tasks):
            group = filter(lambda x: x is not None, group)
            pids = map(lambda t: unicode(t.drm_jobID), group)
            sp.call(['scancel', '-Q'] + pids, preexec_fn=exit_process_group)


def do_sacct(job_ids, log=None, timeout=60 * 10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            # there's a lag between when a job finishes and when sacct is available :(Z
            cmd = 'sacct --format="State,JobID,CPUTime,MaxRSS,AveRSS,AveCPU,CPUTimeRAW,' \
                  'AveVMSize,MaxVMSize,Elapsed,ExitCode,Start,End" -j %s -P' % ','.join(job_ids)
            parts = sp.check_output(cmd,
                                    shell=True, preexec_fn=exit_process_group, stderr=sp.STDOUT
                                    ).decode().strip().split("\n")
            break
        except (sp.CalledProcessError, OSError) as e:  # sometimes slurm goes quiet
            if log:
                log.info('Error running sacct %s' % e)

        time.sleep(10)

    # job_id_to_job_info_dict
    all_jobs = dict()
    # first line is the header
    keys = parts[0].split('|')
    # second line is all dashes, ignore it
    for line in parts[2:]:
        values = line.split('|')
        job_dict = dict(zip(keys, values))

        if 'batch' in job_dict['JobID']:
            # slurm prints these .batch versions of jobids which have better information, overwrite
            job_dict['JobID'] = job_dict['JobID'].replace('.batch', '')

        all_jobs[job_dict['JobID']] = job_dict

    return all_jobs


def parse_sacct(job_info, log=None):
    try:
        job_info2 = job_info.copy()
        if job_info2['State'] in FAILED_STATES + PENDING_STATES:
            job_info2['exit_status'] = None
        else:
            job_info2['exit_status'] = int(job_info2['ExitCode'].split(":")[0])
        job_info2['cpu_time'] = int(job_info2['CPUTimeRAW'])
        job_info2['wall_time'] = (
            parse_slurm_time2(job_info2['End']) - parse_slurm_time2(job_info2['Start'])).total_seconds()
        job_info2['percent_cpu'] = div(float(job_info2['cpu_time']), float(job_info2['wall_time']))
        job_info2['avg_rss_mem'] = convert_size_to_kb(job_info2['AveRSS'])
        job_info2['max_rss_mem'] = convert_size_to_kb(job_info2['MaxRSS'])
        job_info2['avg_vms_mem'] = convert_size_to_kb(job_info2['AveVMSize'])
        job_info2['max_vms_mem'] = convert_size_to_kb(job_info2['MaxVMSize'])
    except Exception as e:
        if log:
            log.info('Error Parsing: %s' % pformat(job_info2))
        raise e

    return job_info2
