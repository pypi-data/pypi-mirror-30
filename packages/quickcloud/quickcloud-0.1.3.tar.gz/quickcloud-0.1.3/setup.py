from distutils.core import setup
setup(
  name = 'quickcloud',
  packages = ['appinstances','common','emails','qsms'], # this must be the same as the name above
  version = '0.1.3',
  description = 'Cloud Manager of QuickCorp',
  author = 'Jean Machuca',
  author_email = 'correojean@gmail.com',
  url = 'https://gitlab.com/quickcorp-pythonapps/cloud.quickcorp.org.git', # use the URL to the github repo
  download_url = 'https://gitlab.com/api/v3/projects/5870429/repository/archive?private_token=Wys-MPRmB1sSFn3eeX84', # I'll explain this in a second
  keywords = ['cloud', 'quickcloud', 'quickcorp','python','app','engine'], # arbitrary keywords
  classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Environment :: Web Environment',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: Python Software Foundation License',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Communications :: Email',
      'Topic :: Office/Business',
      'Topic :: Software Development :: Bug Tracking',
      ],
  install_requires=[
    'django-angular>=1.1',
    'django-chartit>=0.2.9',
    'django-cors-headers>=2.1.0',
    'django-dashing>=0.3.3',
    'django-extra-views>=0.9.0',
    'django-filter>=1.0.4',
    'django-flat-theme>=1.1.4',
    'django-haystack>=2.6.1',
    'django-import-export>=0.5.1',
    'django-localflavor>=1.5.2',
    'django-material>=1.0.0',
    'django-modeladmin-reorder>=0.2',
    'django-mptt>=0.8.7',
    'django-oauth-toolkit>=1.0.0',
    'django-oauth2-provider>=0.2.6.1',
    'django-oscar>=1.5',
    'django-oscar-accounts>=0.3',
    'django-oscar-paypal>=0.9.7',
    'django-paypal>=0.4.1',
    'django-phonenumber-field>=1.3.0',
    'django-simple-import>=2.0.2',
    'django-suit>=0.2.25',
    'django-tables2>=1.10.0',
    'django-treebeard>=4.1.2',
    'django-viewflow>=1.0.2',
    'django-widget-tweaks>=1.4.1',
    'djangorestframework>=3.6.3',
    'djangorestframework-oauth>=1.1.0',
    'BeautifulSoup>=3.2.1',
    'beautifulsoup4>=4.6.0',
    'pyOpenSSL>=17.2.0',
    'qcmaskingcode>=0.1',
    'qrcode>=5.3'
  ]
)
# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
