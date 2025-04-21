#!/bin/bash

# Simple Docker credential helper script
# This outputs an empty JSON credential to stdout to allow Docker to pull public images

echo '{"ServerURL":"https://index.docker.io/v1/","Username":"","Secret":""}' 