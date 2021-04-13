import setuptools
import shutil

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="salamandra",
        version="1.0.1",
        author="Tzachi Noy",
        author_email="tzachi.noy@biu.ac.il",
        description="Framework for netlist manipulation",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/enics-labs/salamandra",
        project_urls={
            "EnICS Labs": "https://enicslabs.com/"
        },
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.5',
        )

# NOTE: Be careful with deleting non-empty folders, this will delete the directory
# no matter what comes after setup.py in your CLI command (every time the script is called or imported).
shutil.rmtree('build', ignore_errors=True)
