# Pytests

run tests with:
```shell
pytest
```

except the slow tests:
```shell
pytest -k "not slow" -v
```

run only slow tests:
```shell
pytest -k slow -v
```

## References

- [Pytest](https://docs.pytest.org/en/7.0.x/)
- [Best Practice](https://www.nerdwallet.com/blog/engineering/5-pytest-best-practices/)