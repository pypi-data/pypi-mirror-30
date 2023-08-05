from aws_acm_cert_validator.logic import AwsAcmCertValidatorLogic
import traceback
import os
import sys
import logging

log = logging.getLogger()
# log.setLevel(logging.DEBUG)

class AwsAcmCertValidatorCli:
    def main(self, domain_name):
        try:
            logic = AwsAcmCertValidatorLogic()
            acm_certificate_arn = logic.request(domain_name=domain_name)
            logic.validate(cert_arn=acm_certificate_arn)
            logic.wait_cert_validated(cert_arn=acm_certificate_arn)
            print(f"\n\n\n{acm_certificate_arn}")
        except Exception as e:
            log.error(f"Failed cert validation and issuance:{e}")
            traceback.print_exc()
            sys.exit(-1)
