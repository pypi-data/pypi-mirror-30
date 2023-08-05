import aws_acm_cert_validator

from aws_acm_cert_validator.main import AwsAcmCertValidatorCli
import logging
import sys


def setup_logging():
    root = logging.getLogger()
    # root.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def main(args=None):
    """The main routine."""
    
    print(f"Aws acm validator v{aws_acm_cert_validator.__version__}")
    
    if args is None:
        args = sys.argv[1:]
    if len(args) != 1:
        print(
        "Usage: aws-acm-cert-validator <domain_name>")
        exit(-2)
    
    setup_logging()
    main_runner = AwsAcmCertValidatorCli()
    main_runner.main(args[0])


if __name__ == "__main__":
    main()
