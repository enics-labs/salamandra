import setuptools
import shutil

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="salamandra",
        version="1.00",
        author="Tzachi Noy",
        author_email="tzachi.noy@biu.ac.il",
        description="Framework for describing hierarchical systems",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="http://enicslabs.com/",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.5',
        )

# NOTE: Be careful with deleting non-empty folders, this will delete the directory
# no matter what comes after setup.py in your CLI command (every time the script is called or imported).
shutil.rmtree('build', ignore_errors=True)
