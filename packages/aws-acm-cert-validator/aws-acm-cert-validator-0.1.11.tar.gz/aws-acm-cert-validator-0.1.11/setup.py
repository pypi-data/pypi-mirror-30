from setuptools import setup

setup(name='aws-acm-cert-validator', version='0.1.11', author='Base2Services R&D',
      author_email='itsupport@base2services.com',
      url='http://github.com/base2Services/cloudformation-custom-resources',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.6',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='aws acm ssl certificate',
      packages=['aws_acm_cert_validator','aws_acm_cert_validator_cli','aws_acm_cert_validator_lambda'],
      install_requires=['boto3'],
      python_requires='>=3.6',
      description='AWS Acm Certificate issuance and validation',
      entry_points={
          'console_scripts': ['aws-acm-cert-validator = aws_acm_cert_validator_cli.__main__:main'],
      })
