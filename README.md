# HomeLab — Lab Documentation

Mixed-architecture Kubernetes homelab (ARM64 Apple Silicon + x86-64).

## Files

| File | Description |
|------|-------------|
| `lab_architecture.html` | Master architecture blueprint (always current) |
| `lab_architecture-ALPHA-005.html` | Architecture blueprint — ALPHA-005 revision (current) |
| `lab_networking-ALPHA-005.html` | Network topology diagrams — Logical, Physical/VLAN, k3s SDN (3 embedded Graphviz SVGs) |
| `build_networking.py` | Reproducible build script — regenerates `lab_networking-ALPHA-005.html` via pygraphviz |

### Archived Revisions
| File | Description |
|------|-------------|
| `lab_architecture-ALPHA-002.html` | Architecture blueprint — ALPHA-002 revision (archived 2026-08-27) |
| `lab_networking-ALPHA-002.html` | Network topology diagrams — ALPHA-002 (archived 2026-08-27) |

## Project
My Local LAB (Mixed Arch k8s) — 16 architectural decisions (AD-001 through AD-016) baselined in ALPHA-005.

### Latest Changes (ALPHA-005)
- AD-016: k3s SDN dual-stack IPv4/IPv6
  - Pod CIDR: 10.42.0.0/16 + fd42::/48
  - Service CIDR: 10.43.0.0/16 + fd43::/112
  - Flannel VXLAN dual-stack, CoreDNS A+AAAA records
  - Scope: k3s SDN overlay only (underlay VLANs remain IPv4)
