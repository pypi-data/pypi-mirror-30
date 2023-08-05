from setuptools import setup

# !!!!!!! MAJOR DEBT - This is hardcoded
VERSION = "0.19.3"

# ~~~~~ Create configuration

setup(
        name='tdl-client-python',
        packages=[
            'tdl',
            'tdl.audit',
            'tdl.queue',
            'tdl.queue.abstractions',
            'tdl.queue.abstractions.response',
            'tdl.queue.actions',
            'tdl.queue.transport',
            'tdl.runner'
        ],
        package_dir={'': 'src'},
        install_requires=['stomp.py==4.1.5','unirest==1.1.7'],
        version=VERSION,
        description='tdl-client-python',
        author='Tim Preece, Julian Ghionoiu',
        author_email='tdpreece@gmail.com, julian.ghionoiu@gmail.com',
        url='https://github.com/julianghionoiu/tdl-client-python',
        download_url='https://github.com/julianghionoiu/tdl-client-python/archive/v{0}.tar.gz'.format(VERSION),
        keywords=['kata', 'activemq', 'rpc'],
        classifiers=[],
)
