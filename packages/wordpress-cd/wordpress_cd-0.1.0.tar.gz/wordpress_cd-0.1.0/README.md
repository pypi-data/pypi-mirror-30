# WordPress Continuous Deployment/Delivery scripts

These scripts are designed to be called as part of the post-commit hook in Git repositories.

Currently tested with:

* GitLab
* Jenkins

I also use the 'build-site' script locally to quickly generate clean builds with certain plugins/themes pre-installed, and use that to kick-start a local development environment.


## Installing the scripts

Install scripts using `pip`:

```
pip install wordpress-cd
```

Or, if deploying from source:

```
python setup.py install
```

Standard stuff. Use 'virtualenv' if you wish.


## Building a WordPress site

First, we define a site configuration by creating a 'config.yml' file.

A sample 'config.yml' file might look like this:

```yaml
# Identifier string that can be used by deployment drivers if required.
id: clubwebsite1

# The main application zipfile to base a build on.
core:
  url: https://wordpress.org/wordpress-4.9.4.tar.gz
  # or perhaps...
  url: https://wordpress.org/wordpress-latest.tar.gz

# List of themes to download and build into the document root
themes:
  - https://downloads.wordpress.org/themes/mobile.zip
  - https://gitlab.com/youraccount/wordpress/themes/acmeltd-theme/repository/master/archive.zip
  - https://s3-eu-west-1.amazonaws.com/yourbucket/production/mobile-child.zip

# 'Must use' plugins
mu-plugins:
  - https://downloads.wordpress.org/plugin/wp-bcrypt.zip

# Ordinary plugins
plugins:
  - https://downloads.wordpress.org/plugin/plugin-groups.zip
  - https://downloads.wordpress.org/plugin/acme-wp-plugin.zip
  - https://downloads.wordpress.org/plugin/another-plugin.zip

# Optional: To put a specific favicon.ico file into place
favicon:
  file: favicon.ico

```

To build a document root that contains a fresh WordPress instance with those themes and plugins installed:

```bash
build-wp-site -v
```

The resulting document root will now exist in the 'build/wordpress' folder.

## Deploying the site

As long as the necessary environment variables are set, it's just a case of running the site deploy script.

```bash
deploy-wp-site -v
```

This script will use the configured deployment driver to deploy the site.

The script needs to know a few things, defined by environment variables. Typically, these variables will be provided by the CI system that's running the script. You can also use the script locally by providing the same environment variables.

Env var | Description | Example value
--------|-------------|--------------
WPCD_JOB_NAME | Typically the short string name of the project/repo being deployed | `acme-widget`
WPCD_GIT_BRANCH | Which branch this is a build of, to help determine which environment to deploy to. | `master` (or `develop`)
WPCD_DRIVERS | Which python modules to import to register the necessary deployment drivers (may load multiple drivers) | `wordpress_cd.drivers.rsync`
WPCD_PLATFORM | Which driver id to use to perform the deployment | `rsync`

The above are the default environment variables used. The deploy script will attempt to identify which CI system is running and use the environment variables specific to that system if found.


### Deployment with rsync

This package comes with a simple 'rsync' based deployment driver. The main environment variables you need to set for a typical rsync deployment are:

Env var | Description | Example value
--------|-------------|--------------
SSH_HOST | Host to rsync to | www.myhost.com
SSH_PORT | (optional) SSH port to rsync to | 22
SSH_USER | Username for SSH connection | www256
SSH_PASS | (optional) Password for SSH connection | topsecret
SSH_PATH | Remote path to deploy to | /var/www/public_html

## Using an alternative deployment driver

You can tell the deployment script to import third-party or custom packages containing alternative deployment drivers by listing the modules to import (comma-seperated) in the `WPCD_DRIVERS` environment variable. The driver that will be chosen for deployment is indicated by the `WPCD_PLATFORM` variable.

```bash
pip install wordpress-cd-rancher
export WPCD_DRIVERS=wordpress_cd_rancher
export WPCD_PLATFORM=rancher
export WPCD_DOCKER_IMAGE=registry.myorganisation.org/project/wordpress:latest
export RANCHER_URL=https://rancher.myorganisation.org
export RANCHER_ACCESS_KEY=blahblah
export RANCHER_SECRET_KEY=sshsshssh
export RANCHER_ENVIRONMENT=1a1
export RANCHER_SERVICE=1s234
deploy-wp-site -v
```


## Integration with CI/CD systems

### GitLab

The deployment script can detect that it is being run in GitLab by the existence of [environment variables](https://docs.gitlab.com/ce/ci/variables/README.html) beginning with 'CI_'.

An example '.gitlab-ci.yml' for a site repository stored on GitLab might look like this:

```yaml
stages:
  - build
  - test
  - deploy

# Fetch an image with the CD scripts ready to run
image: rossigee/wordpress-cd

# Fetch some SSH keys to use for the rsync connection later
before_script:
  - aws s3 sync s3://yourbucket/ssh /root/.ssh && chmod 400 /root/.ssh/id_rsa

# Use the CD image 'build-wp-site' script to prepare the 'build' folder as an artifact
build:
  stage: build
  only:
    - master
  tags:
    - docker
  script:
    - build-wp-site -v
  artifacts:
    paths:
    - build/

# Deploy via rsync for commits to 'master' branch
deploy:
  stage: deploy
  only:
    - master
  tags:
    - docker
  script:
    - deploy-wp-site -v
  environment:
    name: my-wordpress-site
    url: https://www.mysite.com

```

The S3 sync command ensures that the latest SSH public/private keys are available to commands being run in the CD container, without actually distributing those keys in the container image. The script uses the 'aws' command line tool, which depends on the presence of 'AWS_*' environment variables or it's own configuration file.


### Jenkins

The deployment script can detect that it is being run as a Jenkins pipeline by the existence of certain [environment variables](https://wiki.jenkins.io/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-belowJenkinsSetEnvironmentVariables) known to be set by Jenkins.

An example 'Jenkinsfile' for a site might look like this:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'

            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
```
