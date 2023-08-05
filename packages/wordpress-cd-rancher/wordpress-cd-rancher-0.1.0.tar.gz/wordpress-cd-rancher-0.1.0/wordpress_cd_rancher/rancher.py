# Rancher-based deployment functions

import os
import requests
import json
import time
import subprocess
import logging
_logging = logging.getLogger(__name__)

from wordpress_cd.drivers import driver
from wordpress_cd.drivers.base import BaseDriver


@driver('rancher')
class RancherDriver(BaseDriver):
    def __str__(self):
        return "Rancher"

    def __init__(self, args):
        _logging.debug("Initialising Rancher Deployment Driver")
        super(RancherDriver, self).__init__(args)

        self.image_uri = os.environ['WPCD_DOCKER_IMAGE']

    def deploy_site(self):
        _logging.info("Deploying site to Rancher environment (job id: {0})...".format(self.job_id))

        buildargs = ['docker', 'build', '-t', self.image_uri, '.']
        buildenv = os.environ.copy()
        buildproc = subprocess.Popen(buildargs, stderr=subprocess.PIPE, env=buildenv)
        buildproc.wait()
        exitcode = buildproc.returncode
        errmsg = buildproc.stderr.read()
        if exitcode != 0:
            raise Exception("Error while building image: %s" % errmsg)

        pushargs = ['docker', 'push', self.image_uri]
        pushenv = os.environ.copy()
        pushproc = subprocess.Popen(pushargs, stderr=subprocess.PIPE, env=pushenv)
        pushproc.wait()
        exitcode = pushproc.returncode
        errmsg = pushproc.stderr.read()
        if exitcode != 0:
            raise Exception("Error while pushing image: %s" % errmsg)

        projectId = os.environ['RANCHER_ENVIRONMENT']
        serviceId = os.environ['RANCHER_SERVICE']

        # Service endpoint (v2-beta)
        endpoint_url = os.environ['RANCHER_URL'] + '/v2-beta/projects/' + projectId + '/services/' + serviceId
        auth = (os.environ['RANCHER_ACCESS_KEY'], os.environ['RANCHER_SECRET_KEY'])

        # Find service based on the ids provided
        r = requests.get(endpoint_url, auth=auth)
        service = r.json()
        launchConfig = service['launchConfig']
        secondaryLaunchConfigs = service['secondaryLaunchConfigs']

        # Update launchConfig with new image
        launchConfig['imageUuid'] = "docker:" + self.image_uri

        # Construct payload for upgrade
        payload = {
            'inServiceStrategy': {
                'batchSize': 1,
                'intervalMillis': 2000,
                'startFirst': False,
                'launchConfig': launchConfig,
                'secondaryLaunchConfigs': secondaryLaunchConfigs,
            }
        }
        headers = {'content-type': 'application/json'}

        # Upgrade the service with payload
        r = requests.post(endpoint_url + '?action=upgrade',
                          data=json.dumps(payload), headers=headers,
                          auth=auth)

        # Pool service upgrade status
        r = requests.get(endpoint_url, auth=auth)

        state = r.json()['state']
        sleep = 30
        retry = 10

        while (state != 'upgraded'):
            _logging.debug("service: " + service['name'] + " [" + state + "]")
            time.sleep(sleep)
            r = requests.get(endpoint_url, auth=auth)
            state = r.json()['state']
            retry -= 1
            if retry <= 0:
                _logging.error("Maximum retries exceeded")
                return 1
        _logging.debug("service: " + service['name'] + " [upgraded]")

        # Finish Upgrade
        r = requests.post(endpoint_url + '/?action=finishupgrade',
                          headers=headers, auth=auth)

        # Done
        _logging.info("Deployment successful.")
        return 0
