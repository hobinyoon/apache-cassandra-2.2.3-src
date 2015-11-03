## Workload generator for long running applications

### Prerequisite
```
sudo apt-get install -y maven gnuplot-nox
```

### Troubleshootings
#### 1
```
Unexpected error: java.security.InvalidAlgorithmParameterException: the
trustAnchors parameter must be non-empty -> [Help 1]
```
```
$ sudo update-ca-certificates -f
```
Refs: [1](http://stackoverflow.com/questions/4764611/java-security-invalidalgorithmparameterexception-the-trustanchors-parameter-mus)
[2](http://stackoverflow.com/questions/6784463/error-trustanchors-parameter-must-be-non-empty)
