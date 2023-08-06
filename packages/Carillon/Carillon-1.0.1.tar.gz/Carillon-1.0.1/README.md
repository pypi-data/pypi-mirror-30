# Carillon

See PROJECT.rst for basic description and usage

# Development

## Installation

    pip3 install -r requirements.txt

## Testing

Run the script with the default options and icons.

    python3 -m carillon
    
## Deploying

Follow [instructions online](https://packaging.python.org/tutorials/distributing-packages/)
for using PyPi and it's test environment. Then upload:

    ./setup.py sdist upload -r pypitest
    ./setup.py sdist upload -r pypi

# TODO

* Select current keyboard layout on startup
* Create various OS distribution files
