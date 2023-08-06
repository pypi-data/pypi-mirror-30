import os
import uuid
import logging
import yaml
from kubernetes import client, config
from packtivity.asyncbackends import ExternalAsyncBackend
from packtivity.handlers.execution_handlers import command_argv, script_argv

log = logging.getLogger(__name__)
def backend(**opts):
    of = opts.pop('optsyaml',None)
    if of:
        opts.update(**yaml.load(open(of)))
    external = KubernetesBackend(**opts)
    backend  = ExternalAsyncBackend(external)
    return backend

class KubernetesBackend(object):
    def __init__(self,
                 kubeconfigloc = None,
                 incluster = False,
                 stateopts = None,
                 resources_opts = None,
                 resource_labels = None,
                 svcaccount = 'default',
                 namespace = 'default'):
        self.svcaccount = svcaccount
        self.namespace = namespace
        self.stateopts = stateopts or {'type': 'hostpath'}
        self.resource_labels = resource_labels or {'component': 'yadage'}
        self.resources_opts = resources_opts or {
            'requests': {
                'memory': "0.1Gi",
                'cpu': "100m"
            }
        }
        if incluster:
            config.load_incluster_config()
        else:
            config.load_kube_config(kubeconfigloc or os.path.join(os.environ['HOME'],'.kube/config'))
            import urllib3
            urllib3.disable_warnings()

    def submit(self, job, env, state, metadata):
        if 'command' in job:
            stdin = False
            container_argv, container_stdin = command_argv(env,job,log)
        elif 'script' in job:
            stdin = True
            container_argv, container_stdin = script_argv(env,job,log)
            import base64
            encoded = base64.b64encode(container_stdin.encode('utf-8')).decode('utf-8')
            container_argv[-1] = 'echo {}|base64 -d|({})'.format(encoded, container_argv[-1])
        else:
            raise RuntimeError('do not know yet how to run this...')

        specs = self.job_specs(container_argv, env['image'], env['imagetag'], state,
                            cvmfs = 'CVMFS' in env['resources'],
                            parmounts = env['par_mounts'],
                            auth = 'GRIProxy' in env['resources']
                  )
        jobspec    = specs[0]
        configmaps = specs[1:]
        jobid = jobspec['metadata']['name']

        thejob = client.V1Job(
            api_version = jobspec['apiVersion'],
            kind = jobspec['kind'],
            metadata = jobspec['metadata'],
            spec = jobspec['spec']
        )
        client.BatchV1Api().create_namespaced_job(jobspec['metadata']['namespace'],thejob)

        for cm_spec in configmaps:
            cm = client.V1ConfigMap(
                api_version = 'v1',
                kind = 'ConfigMap',
                metadata = {'name': cm_spec['name'], 'namespace': self.namespace, 'labels': self.resource_labels},
                data = cm_spec['data']
            )
            client.CoreV1Api().create_namespaced_config_map(self.namespace,cm)
            log.debug('created configmap for parmounts')


        log.info('submitted job: %s', jobid)
        return {
            'job_id': jobid,
            'configmaps': [c['name'] for c in configmaps]
        }

    def delete_created_resources(self, job_proxy):
        job_id  = job_proxy['job_id']

        try:
            j = client.BatchV1Api().read_namespaced_job(job_id,self.namespace)
            client.BatchV1Api().delete_namespaced_job(job_id,self.namespace,j.spec)
        except client.rest.ApiException:
            pass

        try:
            client.CoreV1Api().delete_collection_namespaced_pod(self.namespace, label_selector = 'job-name={}'.format(job_id))
        except client.rest.ApiException:
            pass

        for c in job_proxy['configmaps']:
            try:
                client.CoreV1Api().delete_namespaced_config_map(c,self.namespace,client.V1DeleteOptions())
            except client.rest.ApiException:
                pass

    def ready(self, job_proxy):
        ready = job_proxy.get('ready',False)
        if ready:
            return True

        job_id  = job_proxy['job_id']
        jobstatus = client.BatchV1Api().read_namespaced_job(job_id,self.namespace).status
        job_proxy['last_success'] = jobstatus.succeeded
        job_proxy['last_failed']  = jobstatus.failed
        ready =  job_proxy['last_success'] or job_proxy['last_failed']
        if ready:
            log.info('job %s is ready. delete. success: %s failed: %s', job_id,
                job_proxy['last_success'], job_proxy['last_failed']
            )
            self.delete_created_resources(job_proxy)
            job_proxy['ready'] = True
        return ready

    def successful(self,resultproxy):
        return True

    def fail_info(self,resultproxy):
        pass

    ## kubespecific methods here
    def state_binds(self, state):
        if self.stateopts['type'] == 'hostpath':
            from .state_hostpath import make_binds
            return make_binds(state, self.stateopts)
        if self.stateopts['type'] == 'sharedvol':
            from .state_sharedvol import make_binds
            return make_binds(state, self.stateopts)
        raise RuntimeError('unknown k8s state type {}'.format(self.stateopts['type']))

    def auth_binds(self):
        container_mounts = []
        volumes = []

        log.debug('binding auth')
        volumes.append({
            'name': 'hepauth',
            'secret': yaml.load(open('secret.yml'))
        })
        container_mounts.append({
            "name": 'hepauth',
            "mountPath": '/recast_auth'
        })
        return container_mounts, volumes

    def cvmfs_binds(self):
        container_mounts = []
        volumes = []
        log.debug('binding CVMFS')
        for repo in ['atlas.cern.ch','sft.cern.ch','atlas-condb.cern.ch']:
            reponame = repo.replace('.','').replace('-','')
            volumes.append({
                'name': reponame,
                'flexVolume': {
                    'driver': "cern/cvmfs",
                    'options': {
                        'repository': repo
                    }
                }
            })
            container_mounts.append({
                "name": reponame,
                "mountPath": '/cvmfs/'+repo
            })
        return container_mounts, volumes

    def make_par_mount(self, job_uuid, parmounts):
        parmount_configmap_contmount = []
        configmapspec = {
            'name': 'parmount-{}'.format(job_uuid),
            'data': {}
        }

        vols_by_dir_name = {}
        for i,x in enumerate(parmounts):
            configkey = 'parmount_{}'.format(i)
            configmapspec['data'][configkey] = x['mountcontent']

            dirname = os.path.dirname(x['mountpath'])
            basename = os.path.basename(x['mountpath'])

            vols_by_dir_name.setdefault(dirname,{
                'name': 'vol-{}'.format(dirname.replace('/','-')),
                'configMap': {
                    'name': configmapspec['name'],
                    'items': []
                }
            })['configMap']['items'].append({
                'key': configkey, 'path': basename
            })

        log.debug(vols_by_dir_name)

        for dirname,volspec in vols_by_dir_name.items():
            parmount_configmap_contmount.append({
                'name': volspec['name'],
                'mountPath':  dirname
            })

        return parmount_configmap_contmount, vols_by_dir_name.values(), configmapspec

    def job_specs(self, argv, image, imagetag,state, cvmfs, parmounts, auth):
        job_uuid = 'wflow-job-{}'.format(str(uuid.uuid4()))

        container_mounts_state, volumes_state = self.state_binds(state)

        container_mounts = container_mounts_state
        volumes = volumes_state

        if cvmfs:
            container_mounts_cvmfs, volumes_cvmfs = self.cvmfs_binds()
            container_mounts += container_mounts_cvmfs
            volumes          += volumes_cvmfs

        if auth:
            container_mounts_auth, volumes_auth = self.auth_binds()
            container_mounts += container_mounts_auth
            volumes          += volumes_auth

        if parmounts:
            container_mounts_pm, volumes_pm, pm_cm_spec = self.make_par_mount(job_uuid, parmounts)
            container_mounts += container_mounts_pm
            volumes += volumes_pm

        specs = []
        specs.append({
          "apiVersion": "batch/v1",
          "kind": "Job",
          "spec": {
            "template": {
              "spec": {
                "serviceAccountName": self.svcaccount,
                "securityContext" : {
                    "runAsUser": 0
                },
                "restartPolicy": "Never",
                "imagePullSecrets": [{"name":"regsecret"}],
                "containers": [
                  {
                    "image": ':'.join([image,imagetag]),
                    "command": argv,
                    "volumeMounts": container_mounts,
                    "name": job_uuid,
                    "resources": self.resources_opts
                  }
                ],
                "volumes": volumes
              },
              "metadata": {
                "name": job_uuid,
                "namespace": self.namespace,
                "labels": self.resource_labels
              }
            }
          },
          "metadata": {
            "name": job_uuid,
            "namespace": self.namespace,
            "labels": self.resource_labels
          }
        })
        if parmounts:
            specs.append(pm_cm_spec)
        return specs
