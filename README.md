Localstack ECS Environment Variable Bug
=======================================

Environment variables don't appear to be propagated into ECS containers in Localstack.

# Reproduction Steps

1. Build Container

```
make
```

This container basically just runs `env` to output the environment it is operating in.

2. Bring up Localstack
```
export LOCALSTACK_API_KEY=XXXXX
docker-compose up
```
Make sure to supply a valid Localstack Pro API key.


3. Run Pulumi
```
cd pulumi
pulumi login --local
export PULUMI_CONFIG_PASSPHRASE=test
pulumi stack init dev
pulumi up
```

This will create a minimal infrastructure including an ECS service
running the container we built earlier.

4. Check Container
```
docker logs -f localstack_testing-family_1
```

You _should_ see the following values in the environment being printed
out, along with other standard values:

```
FOO=BAR
MESSAGE=HELLO WORLD
```
