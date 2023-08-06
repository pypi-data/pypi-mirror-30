from setuptools import setup

setup(
    test_suite="tests",
    packages=[
        "speedwagon",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', "behave", "pytest-qt"],
    python_requires=">=3.6",
)
