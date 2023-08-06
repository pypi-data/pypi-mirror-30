"""Let's Encrypt ACM installer plugin."""

from __future__ import print_function

import logging

import zope.interface

import boto3

from certbot import interfaces
from certbot.plugins import common


logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Plugin):

    description = "ACM installer"

    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Upload Certificate to ACM
        """
        client = boto3.client('acm')
        api_client = boto3.client('apigateway')

        body = open(cert_path).read()
        key = open(key_path).read()
        chain = open(chain_path).read()

        domain_response = api_client.get_domain_name(domainName=domain)
        response = client.import_certificate(
            CertificateArn=domain_response['certificateArn'],
            Certificate=body,
            PrivateKey=key,
            CertificateChain=chain
        )
