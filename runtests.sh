if [ "$LINT" ]; then
    flake8 climata tests
else
    python setup.py test
fi
