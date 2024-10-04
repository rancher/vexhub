# SUSE Rancher - VEX Hub repository

Rancher's VEX Hub repository contains a collection of [VEX]
(Vulnerability-Exploitability eXchange) related reports for Rancher, RKE2, K3s,
Harvester, Longhorn and other container and cloud native solutions images from
SUSE.

For more information about SUSE's VEX Hub initiative, please consult the
knowledge base article [KB 000021573 - How to use SUSE Rancher's VEX Reports].

# Scope

The VEX reports and the CVE statements contained here are **applicable only to
Rancher and other SUSE's container and cloud native products and should not be
used outside of this context**.

# Specification

The VEX report follows the [OpenVEX specification]. The VEX Hub repository follows
Aqua Security's [VEX Repository specification].

# Reports

SUSE's Rancher Prime VEX reports are distributed in two formats:

- A standalone report file: [`rancher.openvex.json`].
- The VEX Hub repository format: [`index.json`].

# How to Use the Reports

The way to consume our VEX reports depends on which CVE scanner is being used.
The following instructions are specific to [Trivy].

## Standalone Report

The [standalone] report contains all the VEX statements. After downloading the
file in its [raw format], you can pass it to Trivy with the `--vex` parameter:
`--vex rancher.openvex.json --show-suppressed`.

```
> trivy image --quiet --scanners vuln --severity CRITICAL --vex rancher.openvex.json --show-suppressed rancher/rancher-agent:v2.9.2

rancher/rancher-agent:v2.9.2 (suse linux enterprise server 15.6)
Total: 0 (CRITICAL: 0)

usr/bin/agent (gobinary)
Total: 0 (CRITICAL: 0)

Suppressed Vulnerabilities (Total: 1)
┌──────────────────────────┬────────────────┬──────────┬──────────────┬─────────────────────────────┬──────────────────────┐
│         Library          │ Vulnerability  │ Severity │    Status    │          Statement          │        Source        │
├──────────────────────────┼────────────────┼──────────┼──────────────┼─────────────────────────────┼──────────────────────┤
│ github.com/docker/docker │ CVE-2024-41110 │ CRITICAL │ not_affected │ vulnerable_code_not_present │ rancher.openvex.json │
└──────────────────────────┴────────────────┴──────────┴──────────────┴─────────────────────────────┴──────────────────────┘
```

**Note:** it's important to manually check if there is a newer version available
of the standalone report, otherwise you might risk missing new VEXed CVEs.

## VEX Hub Repository Format

Using the [VEX Hub repository format] might be an easier way to consume the
reports, as Trivy will take care of updating its local cache copy of the reports
with newer versions available from our VEX Hub.

To configure Trivy to use our VEX Hub, add the following lines to your Trivy's
main configuration file (usually located under the user's home directory in
`$HOME/.trivy/vex/repository.yaml`, please consult Trivy's documentation for
more information).

```
> cat ~/.trivy/vex/repository.yaml
repositories:
  - name: rancher-vexhub
    url: https://github.com/rancher/vexhub
    enabled: true
    username: ""
    password: ""
```

The `url` field must point to our VEX Hub repo at
`https://github.com/rancher/vexhub`.

Verify that Trivy's local VEX Hub database was properly downloaded.

```
> trivy vex repo download
2024-09-25T10:55:28-03:00 INFO [vex] Updating repository... repo="rancher-vexhub" url="https://github.com/rancher/vexhub"
```

Then pass the `--vex repo --show-suppressed` parameters to Trivy.

```
> trivy image --quiet --scanners vuln --severity CRITICAL --vex repo --show-suppressed rancher/rancher-agent:v2.9.2

rancher/rancher-agent:v2.9.2 (suse linux enterprise server 15.6)
Total: 0 (CRITICAL: 0)

usr/bin/agent (gobinary)
Total: 0 (CRITICAL: 0)

Suppressed Vulnerabilities (Total: 1)
┌──────────────────────────┬────────────────┬──────────┬──────────────┬─────────────────────────────┬─────────────────────────────────────┐
│         Library          │ Vulnerability  │ Severity │    Status    │          Statement          │               Source                │
├──────────────────────────┼────────────────┼──────────┼──────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ github.com/docker/docker │ CVE-2024-41110 │ CRITICAL │ not_affected │ vulnerable_code_not_present │ VEX Repository: rancher-vexhub      │
│                          │                │          │              │                             │ (https://github.com/rancher/vexhub) │
└──────────────────────────┴────────────────┴──────────┴──────────────┴─────────────────────────────┴─────────────────────────────────────┘
```

**Note:** when using Trivy's VEX Hub repository feature, your Trivy might
already be configured to use Trivy's default VEX Hub repository that will point
to `https://github.com/aquasecurity/vexhub` instead. The SUSE Rancher Security
team **strongly recommends** that when scanning SUSE Rancher Prime's images to
only use the VEX reports provided here, because we cannot attest VEX reports
from third-parties.

## Use in Air-gap Environments

For instructions on how to use our VEX reports in air-gap environments, please
consult [KB 000021573 - How to use SUSE Rancher's VEX Reports].

# VEXed CVEs

The full list of VEXed CVEs in CSV format is available in [`vex_cves.csv`] for
easy consumption. There it's possible to see all the VEXed vulnerabilities and
their respective statuses and justifications.

# License

The SUSE Rancher VEX data is provided by SUSE under the Creative Commons license
with Attribution (CC-BY-4.0). See the [license] for more information.


<!-- Links -->
[VEX]: https://www.ntia.gov/files/ntia/publications/vex_one-page_summary.pdf
[KB 000021573 - How to use SUSE Rancher's VEX Reports]: https://www.suse.com/support/kb/doc/?id=000021573
[OpenVEX specification]: https://github.com/openvex/spec
[VEX Repository specification]: https://github.com/aquasecurity/vex-repo-spec
[`rancher.openvex.json`]: reports/rancher.openvex.json
[`index.json`]: index.json
[Trivy]: https://github.com/aquasecurity/trivy
[standalone]: reports/rancher.openvex.json
[raw format]: https://raw.githubusercontent.com/rancher/vexhub/refs/heads/main/reports/rancher.openvex.json
[VEX Hub repository format]: reports/rancher.openvex.json
[`vex_cves.csv`]: reports/vex_cves.csv
[license]: LICENSE

