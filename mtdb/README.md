## Workload generator for long running applications

### Prerequisite
```
sudo apt-get install -y maven gnuplot-nox
```

### Troubleshootings
####
```
Unexpected error: java.security.InvalidAlgorithmParameterException: the
trustAnchors parameter must be non-empty -> [Help 1]
```
http://stackoverflow.com/questions/4764611/java-security-invalidalgorithmparameterexception-the-trustanchors-parameter-mus
http://stackoverflow.com/questions/6784463/error-trustanchors-parameter-must-be-non-empty

```
$ sudo update-ca-certificates -f
```

####
```
Error: Could not find or load main class https:..repo.maven.apache.org.maven2.org.apache.maven.plugins.maven-clean-plugin.2.5.maven-clean-plugin-2.5.pom
```

Rebuild dependency file; delete .dep-class-path and try again
```
rm .dep-class-path
```
