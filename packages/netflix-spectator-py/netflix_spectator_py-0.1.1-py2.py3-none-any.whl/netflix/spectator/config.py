def default_config():
    return {
        'frequency': 2,
        'uri': 'http://localhost:7101/publish',
        'common-tags': {
            'nf.app': 'test',
            'nf.cluster': 'test-www',
            'nf.asg': 'test-www-v001',
            'nf.region': 'us-west-1',
        }
    }

def auto_start_global():
    return True