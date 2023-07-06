# Python Tests

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

## Test Status

- [X] Analysis
- [X] Basic
- [X] Cylindrical
- [ ] Simulation
  - [X] Evaluation
    - [ ] Buckling
    - [ ] Eigenfrequency
    - [X] Strength
  - [X] Geometry
  - [X] Shell
  - [X] Stackup

## References

- [Pytest](https://docs.pytest.org/en/7.0.x/)
- [Best Practice](https://www.nerdwallet.com/blog/engineering/5-pytest-best-practices/)
