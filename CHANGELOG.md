# Changelog

All notable changes to this project are recorded here.

## 0.1.0 - 2026-09-02

Initial release.

- Card parser that reads sections, capability claims, and evaluation results.
- Requirements schema with required section resolution.
- Claim to citation resolution, uncited claim detection, metric quote checking,
  and limitation distinctness.
- Gate that passes or refuses a card against a schema.
- Version diff that classifies each change as an added claim, a removed
  limitation, a metric regression, or an editorial change.
