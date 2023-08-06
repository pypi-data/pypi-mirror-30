## ACM installer plugin for [Certbot](https://certbot.eff.org/) client

Use the certbot client to install generated certificate to store
in AWS ACM to be used with an AWS service, like API Gateway.

### Before you start

...

### Setup

The easiest way to install both the certbot client and
the certbot-acm plugin is (not working yet!):
  ```
  pip install certbot-acm
  ```

### How to use it

...

### Automate renewal

To automate the renewal process without prompts (for example,
with a monthly cron), you can add the certbot parameters
`--renew-by-default --text`

### Thanks to

Project [certbot-s3front](https://github.com/dlapiduz/certbot-s3front) is
used as an example.
