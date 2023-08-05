# rancher-autobackup

Do backups from [Rancher](http://rancher.com/) stacks into a git repository.
The [rancher environment](http://rancher.com/docs/rancher/latest/en/environments/) will be commited into a git repository.

## Environment variables

* RANCHER_API_ACCESSKEY
* RANCHER_API_SECRETKEY
* RANCHER_URL
* SSH_PRIVATE_KEY_FILE
* GIT_REPO_SSH_URL
* GIT_USER_EMAIL

## Optional environment variables

* RANCHER_ENVIRONMENT_ID (default: Auto environment id)
* GIT_REPO_BRANCH (default: master)
* GIT_USER_NAME (default: Rancher)
* GIT_COMMIT_MESSAGE (default: autobackup)

## Usage

### docker run

    docker run \
      -e "RANCHER_API_ACCESSKEY=XXXXXXXXXXXXXXXXXXXX" \
      -e "RANCHER_API_SECRETKEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
      -e "RANCHER_URL=https://rancher.server:8080" \
      -e "RANCHER_ENVIRONMENT_ID=1a5" \
      -e "SSH_PRIVATE_KEY_FILE=/run/secrets/id_rancher" \
      -e "GIT_REPO_SSH_URL=ssh://git@github.com:xxx/yyy.git" \
      -e "GIT_USER_EMAIL=autobackup@rancher.com" \
      -v ${PWD}/id_rancher:/run/secrets/id_rancher \
      oscarsix/rancher-autobackup:latest

### docker-compose

    version: '2'
      services:
        autobackup:
          image: oscarsix/rancher-autobackup:latest
          environment:
            RANCHER_API_ACCESSKEY: XXXXXXXXXXXXXXXXXXXX
            RANCHER_API_SECRETKEY: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            RANCHER_URL: https://rancher.server:8080
            SSH_PRIVATE_KEY_FILE: /run/secrets/id_rancher
            GIT_REPO_SSH_URL: ssh://git@github.com:xxx/yyy.git
            GIT_USER_EMAIL: autobackup@rancher.com
          secrets:
            - mode: '0400'
              uid: '0'
              gid: '0'
              source: id_rancher
              target: id_rancher
          labels:
            io.rancher.container.start_once: 'true'
            io.rancher.container.pull_image: always
            cron.schedule: 0 * * * * ?
      secrets:
        id_rancher:
          external: 'true'
