import datetime
import os

from setuptools import setup


def get_version():
    now = datetime.datetime.now()
    start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    secs_since_midnight = (now - start_of_day).seconds
    date = now.strftime("%Y.%m.%d")
    return "{date}.{ssm}".format(date=date, ssm=secs_since_midnight)


setup(
    name='findbugs2junit',
    description='Convert findbugs xml report to junit report',
    long_description=open(os.path.join(os.path.dirname(__file__),
                          "README.rst")).read(),
    url='https://github.com/hughsaunders/findbugs2junit',
    author='Hugh Saunders',
    author_email='hugh@wherenow.org',
    license='Apache',
    packages=["findbugs2junit"],
    python_requires='>=3',
    version=get_version(),
    install_requires=[
        'click==6.7',
        'junit-xml==1.8'
    ],
    entry_points={
        'console_scripts': [
            'findbugs2junit=findbugs2junit.findbugs2junit:cli'
        ]
    }
)
