from setuptools import setup, find_packages


package_name = 'aiostorage'
long_description = (
    'Interface for performing common object storage operations '
    'asynchronously. The aim is to support multiple object storage '
    'providers, e.g. Google Cloud, Backblaze, etc.'
)
version = '0.1.1'
classifiers = [
    'Development Status :: 1 - Planning',

    'Intended Audience :: Developers',

    'Programming Language :: Python :: 3.6',
]
requirements = (
    'aiohttp>=2.0,<3.0',
)

setup(
    name=package_name,
    description='Asynchronous object storage',
    long_description=long_description,

    version=version,
    packages=find_packages(exclude=('tests', )),

    install_requires=requirements,
    classifiers=classifiers,

    author='Guy King',
    author_email='guy@zorncapital.com',
    license='MIT',
    url='https://github.com/family-guy/aiostorage.git',
)

# example usage
# import aiostorage
#
# videos = ('video1.mp4', 'video2.mp4', 'video3.mp4')
# storage = aiostorage.storage(provider='gcloud', auth='auth_details')
# storage.authenticate()
# for video in videos:
#     storage.upload(video, upload_location)
