# mTLS Certificate DOCC job

Renewing mTLS certificates with a DOCC job

## Useful commands

```
docc jobs deploy gencert-staging.json --secret-auth okta
docc jobs list -n platform
docc jobs inspect kea-staging-mtls -n platform
docc jobs logs -j kea-staging-mtls-<job_id> -n platform -s
docc jobs logs -j kea-staging-mtls-27742103 -n platform -s
docc jobs delete kea-staging-mtls -n platform
```

## Enablement

https://github/secrets/pull/2144
