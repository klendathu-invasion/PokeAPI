#!/bin/bash
source scripts/version.sh
sed -e "s/\[APP_VERSION\]/$APP_VERSION/g"  scripts/templates/sonar-project.properties.example > sonar-project.properties
