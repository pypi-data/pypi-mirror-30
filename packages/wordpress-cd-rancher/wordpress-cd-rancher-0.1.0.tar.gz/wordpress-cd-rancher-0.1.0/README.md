# AWS Rancher deployment driver

Packages a site build in a container and deploys it to a Rancher environment.

Requires the '[wordpress-cd](https://github.com/rossigee/wordpress-cd)' package.

Requires the following environment variables to be made available:

Env var | Description | Example
--------|-------------|--------
WPCD_DOCKER_IMAGE | The registry URL to push the container to and to update the Rancher environment to use | registry.gitlab.com/myorganisation/myproject:latest
RANCHER_URL | The Rancher server API URL | https://rancher.myorganisation.com
RANCHER_ACCESS_KEY| The Rancher API access key |
RANCHER_SECRET_KEY| The Rancher API secret key |
RANCHER_ENVIRONMENT | The Rancher environment ID |
RANCHER_SERVICE | The Rancher service ID |

It first invokes 'docker build' to build the image, and 'docker push' to push it to the registry.

Then, it sends an API request to the rancher server to have it upgrade the image in service.
