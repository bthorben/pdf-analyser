setup_args = dict(name="pdfAnalyser",
                  version="0.1",
                  packages=["pdfa"],
                  zip_safe=False)

try:
    from setuptools import setup
    setup_args["entry_points"] = dict(console_scripts=["pdfa=pdfa.main:main"])

except ImportError:
    from distutils.core import setup

setup(**setup_args)
