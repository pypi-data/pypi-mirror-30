from setuptools import setup

try:
    import pypandoc
    README = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    README = ''

setup(
    name='lektor-creative-commons',
    description='Lektor plugin to add Creative Commons license to your pages',
    long_description=README,
    version='0.1.4',
    url='https://github.com/humrochagf/lektor-creative-commons',
    author='Humberto Rocha',
    author_email='humrochagf@gmail.com',
    license='MIT',
    py_modules=['lektor_creative_commons'],
    entry_points={
        'lektor.plugins': [
            'creative-commons = lektor_creative_commons:CreativeCommonsPlugin',
        ]
    }
)
