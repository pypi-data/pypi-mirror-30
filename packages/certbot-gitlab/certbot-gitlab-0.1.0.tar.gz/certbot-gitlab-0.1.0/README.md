# GitLab Pages installer plugin for Certbot

`certbot-gitlab` is an installer plugin for Certbot. It allows you to automate the installation of certificates issued to GitLab Pages domains.

You still need to use a separate authenticator plugin. Read [this](https://certbot.eff.org/docs/using.html#getting-certificates-and-choosing-plugins) for more information on how installer and authenticator plugins.

## Installation

```sh
sudo pip install certbot-gitlab
```

## Usage

### Obtain as access token

[Create an access token](https://gitlab.com/profile/personal_access_tokens) on GitLab with the `api` scope.

### Basic Example

```sh
certbot --installer certbot-gitlab:gitlab
```

This will run Certbot interactively and allow you to choose your specific authentication method.

It will also ask for your GitLab access token. This won't be saved, so automatic renewal (via `certbot renew`) won't work. See [Credentials File](#credentials-file) for how to automate renewal.

If you don't want automatic authentication, then add `--authenticator manual --preferred-challenges dns` to use manual DNS TXT record authentication.

### Credentials File

```sh
certbot --installer certbot-gitlab:gitlab --certbot-gitlab:gitlab-token '/path/to/gitlab/token/file'
```

This will take the GitLab access token from `/path/to/gitlab/token/file`, which should contain just the access token, such as:

```
MY_GITLAB_TOKEN
```

**IMPORTANT**: Make sure this file is in a secure location (such as `/root/` or `/etc/letsencrypt/keys/` and that it can only be read by `root`.

```sh
chown root:root '/path/to/gitlab/token/file'
chmod 600 '/path/to/gitlab/token/file'
```

The path to this file will be saved for automatic renewal, so running `certbot renew` will automatically install the certificate to GitLab when renewed.

### All Options

```
--certbot-gitlab:gitlab-server CERTBOT_GITLAB:GITLAB_SERVER
                      GitLab server url (default: https://gitlab.com)

--certbot-gitlab:gitlab-config CERTBOT_GITLAB:GITLAB_CONFIG
                      python-gitlab configuration file (default: None)

--certbot-gitlab:gitlab-token CERTBOT_GITLAB:GITLAB_TOKEN
                      GitLab API token (default: None)

--certbot-gitlab:gitlab-project CERTBOT_GITLAB:GITLAB_PROJECT
                      Name of GitLab project (e.g. user/proj) (default: None)
```

Read [this](http://python-gitlab.readthedocs.io/en/stable/cli.html#configuration) for how to use `--certbot-gitlab:gitlab-config`.
