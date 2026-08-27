#!/usr/bin/env python3
"""
Build lab_networking-ALPHA-002.html
Three embedded Graphviz SVG diagrams for My Local LAB (Mixed Arch k8s)
Sources: lab_architecture-ALPHA-002 topology
"""

import pygraphviz as pgv
import re, sys
from datetime import datetime

TODAY = "2026-08-27"

# ─────────────────────────────────────────────────────────────────────────────
# SVG helper
# ─────────────────────────────────────────────────────────────────────────────
def make_svg(dot_str, prog="dot"):
    g = pgv.AGraph(string=dot_str)
    g.layout(prog=prog)
    raw = g.draw(format="svg").decode("utf-8")
    raw = re.sub(r"<\?xml[^>]+\?>\s*", "", raw)
    raw = re.sub(r"<!DOCTYPE[^>]+>\s*", "", raw)
    # Make SVG responsive — strip fixed pt dimensions, keep viewBox
    raw = re.sub(
        r'(<svg\s[^>]*?)width="[\d.]+pt"\s+height="[\d.]+pt"',
        r'\1width="100%" style="max-width:100%;height:auto"',
        raw,
    )
    return raw.strip()


# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 1 — LOGICAL TOPOLOGY
# ─────────────────────────────────────────────────────────────────────────────
LOGICAL_DOT = r"""
digraph logical_topology {
    graph [
        bgcolor="#0d1117"
        fontname="Helvetica"
        fontcolor="#e6edf3"
        fontsize=11
        pad=0.7
        nodesep=0.55
        ranksep=0.9
        rankdir=TB
        splines=ortho
        label="Logical Topology  —  My Local LAB (Mixed Arch k8s)\nRef: lab_architecture-ALPHA-002  |  Generated: """ + TODAY + r""""
        labelloc=t
        labeljust=l
    ]
    node [ shape=box style="rounded,filled" fontname="Helvetica" fontcolor="#e6edf3" fontsize=10 penwidth=1.5 margin="0.15,0.1" ]
    edge [ fontname="Helvetica" fontsize=8 fontcolor="#8b949e" color="#444c56" penwidth=1.2 arrowsize=0.7 ]

    // ── External ──
    { rank=source
      internet  [ label="Internet / WAN"                       fillcolor="#1c2128" color="#30363d" ]
      tailscale [ label="Tailscale Overlay\n100.64.0.0/10"     fillcolor="#1c1429" color="#c8b1f5" ]
    }

    // ── Network Core ──
    router  [ label="Mikrotik RouterOS  Core Router\nOSPF · BGP · WireGuard · NAT · FW"   fillcolor="#0c2d48" color="#1f6feb" ]
    sw10g   [ label="10 GbE Switch\nVLAN Trunk · LACP · MTU 9000 · EEE off"               fillcolor="#0c2d48" color="#1f6feb" ]
    haproxy [ label="HAProxy + Keepalived\nVIP 10.10.20.100\nVRRP <1 s · L7 HTTPS · L4 :6443\nStats :8404"  fillcolor="#0a1f0e" color="#3fb950" ]

    // ── ARM64 Compute ──
    subgraph cluster_arm {
        label="ARM64 Compute — Apple Mac Mini"
        style="rounded,filled" fillcolor="#0d1f10" color="#3fb950" fontcolor="#3fb950" fontsize=9
        mmcp   [ label="mm-cp\nk3s Control Plane\netcd embedded\n10.10.0.10"  fillcolor="#122d1a" color="#3fb950" ]
        mmw1   [ label="mm-w1\nk3s Worker ARM64\n10.10.0.11"                  fillcolor="#122d1a" color="#3fb950" ]
        mmw2   [ label="mm-w2\nk3s Worker ARM64\n10.10.0.12"                  fillcolor="#122d1a" color="#3fb950" ]
        tbmesh [ label="Thunderbolt 4 Mesh\n192.168.100.0/24 · 40 Gb/s · MTU 9000" fillcolor="#0a1f0e" color="#3fb950" shape=parallelogram ]
    }

    // ── x86-64 Compute ──
    subgraph cluster_x86 {
        label="x86-64 Compute — ESXi + Proxmox"
        style="rounded,filled" fillcolor="#0d1f2d" color="#58a6ff" fontcolor="#58a6ff" fontsize=9
        esxi1 [ label="ESXi Host 1\nvSphere 8.x · VCSA\n10.10.10.101"              fillcolor="#0c2a3d" color="#58a6ff" ]
        esxi2 [ label="ESXi Host 2\nvSphere HA/DRS\n10.10.10.102"                  fillcolor="#0c2a3d" color="#58a6ff" ]
        pve   [ label="Proxmox Cluster\nPVE 8.x · 3-node · Corosync\n10.10.10.111-113"  fillcolor="#0c2a3d" color="#58a6ff" ]
        x86w  [ label="x86-w1 / x86-w2\nk3s Workers AMD64\n10.10.0.20-21"         fillcolor="#0c2a3d" color="#58a6ff" ]
    }

    // ── Storage ──
    subgraph cluster_stor {
        label="Storage — VLAN 30  10.10.30.0/24  MTU 9000"
        style="rounded,filled" fillcolor="#0d1b2a" color="#79c0ff" fontcolor="#79c0ff" fontsize=9
        nfs   [ label="NFS Server\nRHEL 8 · NFSv4.1\n10.10.30.10"               fillcolor="#0c2030" color="#79c0ff" ]
        iscsi [ label="iSCSI Target LIO\nLVM-thin · MPIO 2-path\n10.10.30.20:3260" fillcolor="#0c2030" color="#79c0ff" ]
        minio [ label="MinIO (S3)\nTLS · :9000/:9001\n10.10.30.30"                fillcolor="#0c2030" color="#79c0ff" ]
        ceph  [ label="Ceph (Proxmox)\nNVMe OSDs · Replica 2/3"                   fillcolor="#0c2030" color="#79c0ff" ]
    }

    // ── Identity & PKI ──
    subgraph cluster_id {
        label="Identity & PKI — VLAN 10"
        style="rounded,filled" fillcolor="#1c1429" color="#c8b1f5" fontcolor="#c8b1f5" fontsize=9
        ad       [ label="Active Directory\nlab.local · WinSrv 2022\n10.10.10.5"                 fillcolor="#221733" color="#c8b1f5" ]
        freeipa  [ label="FreeIPA\nLDAP · Kerberos · DNS\nSSSD all Linux · 10.10.10.6"            fillcolor="#221733" color="#c8b1f5" ]
        keycloak [ label="Keycloak SSO\nOIDC · SAML 2.0\nsso.lab.local"                          fillcolor="#221733" color="#c8b1f5" ]
        pki      [ label="Internal PKI (step-ca)\nRoot→Intermediate · ACME\nSSH CA · ca.lab.local" fillcolor="#221733" color="#c8b1f5" ]
    }

    // ── Databases ──
    subgraph cluster_db {
        label="Databases — VLAN 20"
        style="rounded,filled" fillcolor="#1c1414" color="#ffa198" fontcolor="#ffa198" fontsize=9
        mariadb  [ label="MariaDB Galera\n3-node · VIP 10.10.20.200:3306"   fillcolor="#2a1414" color="#ffa198" ]
        oracle   [ label="Oracle 19c/21c\nRHEL 8 VM · :1521 · SID LABDB\n10.10.20.60" fillcolor="#2a1414" color="#ffa198" ]
        postgres [ label="PostgreSQL\n:5432 · Keycloak + Apps"               fillcolor="#2a1414" color="#ffa198" ]
    }

    // ── Observability ──
    subgraph cluster_obs {
        label="Observability — VLAN 20"
        style="rounded,filled" fillcolor="#0d1f1f" color="#39d353" fontcolor="#39d353" fontsize=9
        elastic    [ label="Elasticsearch\n3-node · X-Pack · ILM 90d\n10.10.20.70:9200"  fillcolor="#0c2020" color="#39d353" ]
        kibana     [ label="Kibana\nSAML SSO · kibana.lab.local"                          fillcolor="#0c2020" color="#39d353" ]
        logstash   [ label="Logstash\n+ Filebeat DaemonSet"                               fillcolor="#0c2020" color="#39d353" ]
        prometheus [ label="Prometheus\nkube-prom-stack · node-exporter\nall arches"      fillcolor="#0c2020" color="#39d353" ]
        grafana    [ label="Grafana\nOIDC SSO · grafana.lab.local"                        fillcolor="#0c2020" color="#39d353" ]
    }

    // ── Edges ──
    internet  -> router  [ label="WAN · BGP/NAT" ]
    tailscale -> router  [ label="subnet router\n100.64.0.0/10" color="#c8b1f5" style=dashed ]

    router  -> sw10g   [ label="L3 trunk · all VLANs" penwidth=2 ]
    sw10g   -> haproxy [ label="VLAN 20\n:80/:443/:6443"  color="#3fb950" penwidth=2 ]
    sw10g   -> mmcp    [ label="VLAN 20"     color="#3fb950" ]
    sw10g   -> mmw1    [ label="VLAN 20"     color="#3fb950" ]
    sw10g   -> mmw2    [ label="VLAN 20"     color="#3fb950" ]
    sw10g   -> esxi1   [ label="VLAN trunk"  color="#58a6ff" ]
    sw10g   -> esxi2   [ label="VLAN trunk"  color="#58a6ff" ]
    sw10g   -> pve     [ label="VLAN trunk"  color="#58a6ff" ]
    sw10g   -> x86w    [ label="VLAN 20"     color="#58a6ff" ]
    haproxy -> mmcp    [ label="K8s API :6443\nVRRP load-balanced" color="#3fb950" penwidth=2 ]

    mmcp -> tbmesh [ color="#3fb950" penwidth=2.5 style=bold ]
    mmw1 -> tbmesh [ color="#3fb950" penwidth=2.5 style=bold ]
    mmw2 -> tbmesh [ color="#3fb950" penwidth=2.5 style=bold ]

    esxi1 -> nfs   [ label="NFSv4.1\nVLAN 30" color="#79c0ff" ]
    esxi1 -> iscsi [ label="iSCSI MPIO\nVLAN 30" color="#79c0ff" ]
    esxi2 -> nfs   [ color="#79c0ff" ]
    esxi2 -> iscsi [ color="#79c0ff" ]
    pve   -> nfs   [ label="NFSv4.1" color="#79c0ff" ]
    pve   -> ceph  [ label="OSD replication" color="#79c0ff" penwidth=2 ]
    x86w  -> nfs   [ label="k8s PVCs RWX"    color="#79c0ff" ]
    mmw1  -> nfs   [ label="k8s PVCs"        color="#79c0ff" ]
    mmw2  -> nfs   [ color="#79c0ff" ]

    ad      -> freeipa  [ label="cross-realm trust" color="#c8b1f5" ]
    freeipa -> keycloak [ label="LDAP broker"       color="#c8b1f5" ]
    ad      -> keycloak [ label="LDAP broker"       color="#c8b1f5" ]
    pki     -> freeipa  [ label="CA integration"    color="#c8b1f5" ]
    keycloak -> grafana  [ label="OIDC"  color="#c8b1f5" style=dashed ]
    keycloak -> kibana   [ label="SAML"  color="#c8b1f5" style=dashed ]
    keycloak -> postgres [ label="backend DB"        color="#ffa198" ]

    prometheus -> grafana  [ label="datasource" ]
    logstash   -> elastic  [ label="index"       ]
    elastic    -> kibana   [ label="query"        ]
    oracle     -> minio    [ label="RMAN backups" color="#79c0ff" style=dashed ]
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 2 — PHYSICAL / VLAN MAP
# ─────────────────────────────────────────────────────────────────────────────
VLAN_DOT = r"""
digraph physical_vlan {
    graph [
        bgcolor="#0d1117"
        fontname="Helvetica"
        fontcolor="#e6edf3"
        fontsize=11
        pad=0.7
        nodesep=0.45
        ranksep=0.8
        rankdir=TB
        splines=polyline
        label="Physical / VLAN Map  —  My Local LAB\nVLAN 10: Mgmt  ·  VLAN 20: VM LAN  ·  VLAN 30: Storage (MTU 9000)  ·  VLAN 40: vMotion (MTU 9000)  ·  VLAN 50: DMZ"
        labelloc=t
        labeljust=l
    ]
    node [ shape=box style="rounded,filled" fontname="Helvetica" fontcolor="#e6edf3" fontsize=9 penwidth=1.4 margin="0.12,0.08" ]
    edge [ fontname="Helvetica" fontsize=7 fontcolor="#8b949e" color="#444c56" penwidth=1.0 arrowsize=0.6 ]

    // Physical backbone
    { rank=source
      internet [ label="Internet / WAN" fillcolor="#1c2128" color="#30363d" fontsize=10 ] }
    router [ label="Mikrotik RouterOS · Core Router\nOSPF · BGP · WireGuard · FW · NAT" fillcolor="#0c2d48" color="#1f6feb" fontsize=10 ]
    sw10g  [ label="10 GbE Switch · VLAN Trunk\nLACP · MTU 9000 · EEE disabled"          fillcolor="#0c2d48" color="#1f6feb" fontsize=10 ]
    internet -> router [ label="WAN" ]
    router   -> sw10g  [ label="L3 trunk · all VLANs" penwidth=2 ]

    // VLAN 10 — Management
    subgraph cluster_v10 {
        label="VLAN 10 — Management  10.10.10.0/24"
        style="rounded,filled" fillcolor="#0c1830" color="#1f6feb" fontcolor="#79c0ff" fontsize=9
        v10_mmcp  [ label="mm-cp\n10.10.0.10"          fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_mmw1  [ label="mm-w1\n10.10.0.11"          fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_mmw2  [ label="mm-w2\n10.10.0.12"          fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_e1    [ label="ESXi Host 1\n10.10.10.101"  fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_e2    [ label="ESXi Host 2\n10.10.10.102"  fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_pve1  [ label="PVE Node 1\n10.10.10.111"   fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_pve2  [ label="PVE Node 2\n10.10.10.112"   fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_pve3  [ label="PVE Node 3\n10.10.10.113"   fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_ad    [ label="Active Directory\n10.10.10.5"  fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_ipa   [ label="FreeIPA\n10.10.10.6"        fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_x1    [ label="x86-w1\n10.10.0.20"         fillcolor="#0c2a3d" color="#1f6feb" ]
        v10_x2    [ label="x86-w2\n10.10.0.21"         fillcolor="#0c2a3d" color="#1f6feb" ]
    }

    // VLAN 20 — VM LAN
    subgraph cluster_v20 {
        label="VLAN 20 — VM LAN  10.10.20.0/24"
        style="rounded,filled" fillcolor="#0d1f10" color="#3fb950" fontcolor="#3fb950" fontsize=9
        v20_hap  [ label="HAProxy VIP\n10.10.20.100"           fillcolor="#122d1a" color="#3fb950" ]
        v20_kc   [ label="Keycloak SSO\nsso.lab.local"         fillcolor="#122d1a" color="#3fb950" ]
        v20_mdb  [ label="MariaDB Galera\nVIP 10.10.20.200:3306" fillcolor="#2a1414" color="#ffa198" ]
        v20_ora  [ label="Oracle DB\n10.10.20.60:1521"         fillcolor="#2a1414" color="#ffa198" ]
        v20_pg   [ label="PostgreSQL\n:5432"                   fillcolor="#2a1414" color="#ffa198" ]
        v20_es   [ label="Elasticsearch\n10.10.20.70:9200"     fillcolor="#0c2020" color="#39d353" ]
        v20_kb   [ label="Kibana\nkibana.lab.local"            fillcolor="#0c2020" color="#39d353" ]
        v20_gr   [ label="Grafana\ngrafana.lab.local"          fillcolor="#0c2020" color="#39d353" ]
        v20_pr   [ label="Prometheus\nkube-prom-stack"         fillcolor="#0c2020" color="#39d353" ]
        v20_pki  [ label="step-ca PKI\nca.lab.local"           fillcolor="#221733" color="#c8b1f5" ]
    }

    // VLAN 30 — Storage
    subgraph cluster_v30 {
        label="VLAN 30 — Storage  10.10.30.0/24  MTU 9000"
        style="rounded,filled" fillcolor="#0d1b2a" color="#79c0ff" fontcolor="#79c0ff" fontsize=9
        v30_nfs   [ label="NFS Server RHEL 8\n10.10.30.10  NFSv4.1"             fillcolor="#0c2030" color="#79c0ff" ]
        v30_iscsi [ label="iSCSI Target LIO\n10.10.30.20:3260  MPIO 2-path"     fillcolor="#0c2030" color="#79c0ff" ]
        v30_minio [ label="MinIO S3\n10.10.30.30  :9000/:9001"                  fillcolor="#0c2030" color="#79c0ff" ]
        v30_e1s   [ label="ESXi Host 1\nstorage NIC  10.10.30.101"              fillcolor="#0c2030" color="#79c0ff" ]
        v30_e2s   [ label="ESXi Host 2\nstorage NIC  10.10.30.102"              fillcolor="#0c2030" color="#79c0ff" ]
        v30_ceph  [ label="Ceph (Proxmox)\nNVMe OSDs · Replica 2/3"             fillcolor="#0c2030" color="#79c0ff" ]
    }

    // VLAN 40 — vMotion
    subgraph cluster_v40 {
        label="VLAN 40 — vMotion  10.10.40.0/24  MTU 9000"
        style="rounded,filled" fillcolor="#1f1a0d" color="#e3b341" fontcolor="#e3b341" fontsize=9
        v40_e1 [ label="ESXi Host 1\nvMotion  10.10.40.101"  fillcolor="#2a2010" color="#e3b341" ]
        v40_e2 [ label="ESXi Host 2\nvMotion  10.10.40.102"  fillcolor="#2a2010" color="#e3b341" ]
    }

    // VLAN 50 — DMZ
    subgraph cluster_v50 {
        label="VLAN 50 — DMZ  10.10.50.0/24  (Reserved)"
        style="rounded,filled" fillcolor="#1f0d0d" color="#f85149" fontcolor="#f85149" fontsize=9
        v50_dmz [ label="DMZ Services\n(TBD — AD-TBD)" fillcolor="#2a1010" color="#f85149" style="rounded,filled,dashed" ]
    }

    // Thunderbolt 4 mesh
    subgraph cluster_tb {
        label="Thunderbolt 4 Mesh — 192.168.100.0/24  40 Gb/s  MTU 9000  (ARM64 private backbone)"
        style="rounded,filled" fillcolor="#0a1a0a" color="#3fb950" fontcolor="#3fb950" fontsize=9
        tb_cp [ label="mm-cp  192.168.100.1"  fillcolor="#0d2010" color="#3fb950" ]
        tb_w1 [ label="mm-w1  192.168.100.2"  fillcolor="#0d2010" color="#3fb950" ]
        tb_w2 [ label="mm-w2  192.168.100.3"  fillcolor="#0d2010" color="#3fb950" ]
        tb_cp -> tb_w1 [ label="TB4 40 Gb/s" dir=both color="#3fb950" penwidth=2.5 style=bold ]
        tb_cp -> tb_w2 [ label="TB4 40 Gb/s" dir=both color="#3fb950" penwidth=2.5 style=bold ]
        tb_w1 -> tb_w2 [ label="TB4 40 Gb/s" dir=both color="#3fb950" penwidth=2.5 style=bold ]
    }

    // Tailscale overlay
    subgraph cluster_ts {
        label="Tailscale Overlay — 100.64.0.0/10  (WireGuard mesh)"
        style="rounded,filled" fillcolor="#1c1429" color="#c8b1f5" fontcolor="#c8b1f5" fontsize=9
        ts_rt [ label="Subnet Router\n-> 10.10.0.0/16\nMagicDNS lab.local  ACL default-deny"  fillcolor="#221733" color="#c8b1f5" ]
        ts_cl [ label="Cloud Burst Nodes\nAWS / Azure / GCP\n(Tailscale peers  AD-014 TBD)"    fillcolor="#221733" color="#c8b1f5" style="rounded,filled,dashed" ]
        ts_rt -> ts_cl [ color="#c8b1f5" style=dashed ]
    }

    // Switch -> VLANs
    sw10g -> v10_mmcp  [ label="VLAN 10"           color="#1f6feb" ]
    sw10g -> v10_e1    [ label="VLAN 10"           color="#1f6feb" ]
    sw10g -> v10_pve1  [ label="VLAN 10"           color="#1f6feb" ]
    sw10g -> v20_hap   [ label="VLAN 20"           color="#3fb950" penwidth=1.8 ]
    sw10g -> v30_nfs   [ label="VLAN 30  MTU 9000" color="#79c0ff" ]
    sw10g -> v30_e1s   [ label="VLAN 30  MTU 9000" color="#79c0ff" ]
    sw10g -> v40_e1    [ label="VLAN 40  MTU 9000" color="#e3b341" ]
    sw10g -> v40_e2    [ label="VLAN 40  MTU 9000" color="#e3b341" ]
    router -> ts_rt    [ label="WireGuard\n100.64.0.0/10" color="#c8b1f5" style=dashed ]

    // Storage fabric
    v30_e1s  -> v30_nfs   [ label="NFSv4.1"    color="#79c0ff" ]
    v30_e1s  -> v30_iscsi [ label="iSCSI"       color="#79c0ff" ]
    v30_e2s  -> v30_nfs   [ color="#79c0ff" ]
    v30_e2s  -> v30_iscsi [ color="#79c0ff" ]
    v30_ceph -> v30_nfs   [ label="OSD repl"    color="#79c0ff" style=dashed ]

    // vMotion path
    v40_e1 -> v40_e2 [ label="vMotion  DRS" dir=both color="#e3b341" style=dashed penwidth=2 ]

    // Identity chain
    v10_ad  -> v10_ipa  [ label="cross-realm" color="#c8b1f5" style=dashed ]
    v10_ipa -> v20_kc   [ label="LDAP broker" color="#c8b1f5" style=dashed ]
    v10_ad  -> v20_kc   [ label="LDAP broker" color="#c8b1f5" style=dashed ]

    // Backup
    v20_ora -> v30_minio [ label="RMAN -> MinIO" color="#79c0ff" style=dashed ]
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 3 — k3s CLUSTER SDN + NODE / WORKLOAD VIEW
# ─────────────────────────────────────────────────────────────────────────────
K8S_DOT = r"""
digraph k8s_cluster {
    graph [
        bgcolor="#0d1117"
        fontname="Helvetica"
        fontcolor="#e6edf3"
        fontsize=11
        pad=0.7
        nodesep=0.65
        ranksep=0.95
        rankdir=TB
        splines=curved
        label="k3s Cluster — SDN & Node / Workload View\nPod CIDR: 10.42.0.0/16  ·  Service CIDR: 10.43.0.0/16  ·  CNI: Flannel VXLAN"
        labelloc=t
        labeljust=l
    ]
    node [ shape=box style="rounded,filled" fontname="Helvetica" fontcolor="#e6edf3" fontsize=9 penwidth=1.5 margin="0.15,0.1" ]
    edge [ fontname="Helvetica" fontsize=8 fontcolor="#8b949e" color="#444c56" penwidth=1.1 arrowsize=0.65 ]

    // External entry
    { rank=source
      inet_client [ label="Clients / Internet" fillcolor="#1c2128" color="#30363d" ]
    }
    haproxy [ label="HAProxy + Keepalived\nVIP 10.10.20.100\nK8s API :6443  L7 HTTPS :443" fillcolor="#0a1f0e" color="#3fb950" fontsize=10 ]
    inet_client -> haproxy [ label=":443 / :6443" ]

    // External dependencies
    ext_stor [ label="Storage Backends\nNFS  10.10.30.10  (RWX  NFSv4.1)\niSCSI  10.10.30.20  (RWO  LVM-thin  MPIO)\nCeph on Proxmox  (RWO)" fillcolor="#0d1b2a" color="#79c0ff" ]
    ext_id   [ label="FreeIPA  10.10.10.6\nLDAP · Kerberos · DNS\nSSSD on all Linux hosts"  fillcolor="#1c1429" color="#c8b1f5" ]
    ext_ad   [ label="Active Directory  10.10.10.5\nlab.local  WinSrv 2022"                  fillcolor="#1c1429" color="#c8b1f5" ]
    ext_ad -> ext_id [ label="cross-realm trust" color="#c8b1f5" style=dashed ]

    // Control Plane
    subgraph cluster_cp {
        label="Control Plane — ARM64  (Apple Mac Mini)"
        style="rounded,filled" fillcolor="#0d1f10" color="#3fb950" fontcolor="#3fb950" fontsize=9
        mmcp [ label="mm-cp  ARM64\nVLAN 20: 10.10.0.10\nTB4 mesh: 192.168.100.1\n─────────────\nk3s server\netcd  embedded  single-node\nkube-apiserver  kube-scheduler\nkube-controller-manager\nflannel VXLAN agent\nCoreDNS  :53" fillcolor="#122d1a" color="#3fb950" ]
    }

    // ARM64 Workers
    subgraph cluster_armwk {
        label="Workers — ARM64  (label: kubernetes.io/arch=arm64)"
        style="rounded,filled" fillcolor="#0d1f10" color="#3fb950" fontcolor="#3fb950" fontsize=9
        mmw1 [ label="mm-w1  ARM64\n10.10.0.11  /  192.168.100.2\n─────────────\nk3s agent  containerd\nQEMU binfmt (x86 emul)\nflannel VXLAN\n─────────────\nWorkloads:\nPrometheus + Grafana\nKeycloak SSO\nstep-ca PKI" fillcolor="#122d1a" color="#3fb950" ]
        mmw2 [ label="mm-w2  ARM64\n10.10.0.12  /  192.168.100.3\n─────────────\nk3s agent  containerd\nQEMU binfmt (x86 emul)\nflannel VXLAN\n─────────────\nWorkloads:\nLogstash\nFilebeat DaemonSet\nMinIO client ops"     fillcolor="#122d1a" color="#3fb950" ]
    }

    // x86 Workers
    subgraph cluster_x86wk {
        label="Workers — AMD64  (taint: arch=amd64:NoSchedule)"
        style="rounded,filled" fillcolor="#0d1f2d" color="#58a6ff" fontcolor="#58a6ff" fontsize=9
        x86w1 [ label="x86-w1  AMD64\n10.10.0.20  VLAN 20\n─────────────\nk3s agent  containerd\nQEMU binfmt (ARM emul)\nflannel VXLAN\n─────────────\nWorkloads:\nMariaDB Galera node-1\nElasticsearch node-1" fillcolor="#0c2a3d" color="#58a6ff" ]
        x86w2 [ label="x86-w2  AMD64\n10.10.0.21  VLAN 20\n─────────────\nk3s agent  containerd\nQEMU binfmt (ARM emul)\nflannel VXLAN\n─────────────\nWorkloads:\nMariaDB Galera node-2\nElasticsearch node-2\nKibana" fillcolor="#0c2a3d" color="#58a6ff" ]
    }

    // SDN overlay
    subgraph cluster_sdn {
        label="Cluster SDN — Flannel VXLAN Overlay"
        style="rounded,filled" fillcolor="#0d1429" color="#c8b1f5" fontcolor="#c8b1f5" fontsize=9
        pod_net [ label="Pod Network  10.42.0.0/16\nFlannel VXLAN  UDP :8472\nper-node /24 slice"     fillcolor="#1c1a2d" color="#c8b1f5" shape=parallelogram ]
        svc_net [ label="Service Network  10.43.0.0/16\nkube-proxy  iptables\nClusterIP · NodePort · LB" fillcolor="#1c1a2d" color="#c8b1f5" shape=parallelogram ]
        coredns [ label="CoreDNS  10.43.0.10\nCluster DNS\nUpstream -> FreeIPA :53"                    fillcolor="#1c1a2d" color="#c8b1f5" ]
    }

    // Storage classes
    subgraph cluster_sc {
        label="Storage Classes — PVC Bindings"
        style="rounded,filled" fillcolor="#0d1b2a" color="#79c0ff" fontcolor="#79c0ff" fontsize=9
        sc_nfs   [ label="nfs-client\nRWX\nnfs-subdir-provisioner"  fillcolor="#0c2030" color="#79c0ff" ]
        sc_iscsi [ label="iscsi-lvmthin\nRWO\nopeniscsi CSI"         fillcolor="#0c2030" color="#79c0ff" ]
        sc_ceph  [ label="ceph-rbd\nRWO\nrook-ceph CSI"              fillcolor="#0c2030" color="#79c0ff" ]
    }

    // TB4 mesh backbone
    tbmesh [ label="Thunderbolt 4 Mesh  192.168.100.0/24\n40 Gb/s · MTU 9000 · point-to-point\ncp <-> w1 · cp <-> w2 · w1 <-> w2\netcd quorum · pod overlay · high-BW intra-ARM" fillcolor="#0a1f0e" color="#3fb950" shape=parallelogram fontsize=9 ]

    // Edges
    haproxy -> mmcp  [ label="API :6443\nVRRP load-balanced" color="#3fb950" penwidth=2.5 ]

    mmcp -> mmw1  [ label="kubelet :10250\nVLAN 20" color="#3fb950" ]
    mmcp -> mmw2  [ label="kubelet :10250"           color="#3fb950" ]
    mmcp -> x86w1 [ label="kubelet :10250\nVLAN 20" color="#58a6ff" ]
    mmcp -> x86w2 [ label="kubelet :10250"           color="#58a6ff" ]

    mmcp -> tbmesh [ color="#3fb950" penwidth=3 style=bold ]
    mmw1 -> tbmesh [ color="#3fb950" penwidth=3 style=bold ]
    mmw2 -> tbmesh [ color="#3fb950" penwidth=3 style=bold ]

    mmcp  -> pod_net [ color="#c8b1f5" style=dashed ]
    mmw1  -> pod_net [ color="#c8b1f5" style=dashed ]
    mmw2  -> pod_net [ color="#c8b1f5" style=dashed ]
    x86w1 -> pod_net [ color="#c8b1f5" style=dashed ]
    x86w2 -> pod_net [ color="#c8b1f5" style=dashed ]
    pod_net -> svc_net [ color="#c8b1f5" ]
    svc_net -> coredns [ color="#c8b1f5" ]
    coredns -> ext_id  [ label="upstream DNS\n.lab.local zone" color="#c8b1f5" style=dashed ]
    ext_id  -> mmcp    [ label="SSSD / Kerberos\nhost auth"    color="#c8b1f5" style=dashed ]

    sc_nfs   -> ext_stor [ label="NFSv4.1"   color="#79c0ff" ]
    sc_iscsi -> ext_stor [ label="iSCSI MPIO" color="#79c0ff" ]
    sc_ceph  -> ext_stor [ label="Ceph RBD"  color="#79c0ff" ]

    mmw1  -> sc_nfs   [ label="RWX PVCs" color="#79c0ff" style=dashed ]
    mmw2  -> sc_nfs   [ color="#79c0ff" style=dashed ]
    x86w1 -> sc_iscsi [ label="RWO PVCs" color="#79c0ff" style=dashed ]
    x86w2 -> sc_iscsi [ color="#79c0ff" style=dashed ]
    x86w1 -> sc_ceph  [ color="#79c0ff" style=dashed ]
    x86w2 -> sc_ceph  [ color="#79c0ff" style=dashed ]
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Generate SVGs
# ─────────────────────────────────────────────────────────────────────────────
print("Generating SVGs...", flush=True)
svg_logical = make_svg(LOGICAL_DOT, prog="dot")
print("  [1/3] logical topology — OK", flush=True)
svg_vlan = make_svg(VLAN_DOT, prog="dot")
print("  [2/3] physical/VLAN — OK", flush=True)
svg_k8s = make_svg(K8S_DOT, prog="dot")
print("  [3/3] k8s cluster — OK", flush=True)

# ─────────────────────────────────────────────────────────────────────────────
# HTML page
# ─────────────────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lab Networking — ALPHA-002</title>
<style>
  :root {{
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #21262d;
    --border:    #30363d;
    --text:      #e6edf3;
    --text-muted:#8b949e;
    --accent:    #1f6feb;
    --green:     #3fb950;
    --blue:      #58a6ff;
    --cyan:      #79c0ff;
    --purple:    #c8b1f5;
    --yellow:    #e3b341;
    --red:       #f85149;
    --pink:      #ffa198;
    --teal:      #39d353;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 13px; line-height: 1.5; }}

  /* ── HEADER ── */
  .page-header {{
    background: linear-gradient(135deg, #0c1f3b 0%, #0d1117 60%);
    border-bottom: 1px solid var(--border);
    padding: 18px 28px 14px;
  }}
  .page-header h1 {{ font-size: 20px; font-weight: 700; color: var(--text); letter-spacing: 0.3px; }}
  .page-header h1 span {{ color: var(--accent); }}
  .meta-row {{ display: flex; gap: 24px; margin-top: 8px; flex-wrap: wrap; }}
  .meta-item {{ color: var(--text-muted); font-size: 11px; }}
  .meta-item strong {{ color: var(--text); }}
  .badge {{
    display: inline-block; padding: 1px 7px; border-radius: 10px;
    font-size: 10px; font-weight: 600; background: #1c3a5f; color: var(--cyan);
    border: 1px solid #1f6feb44; vertical-align: middle;
  }}
  .xref-link {{ color: var(--accent); text-decoration: none; font-size: 11px; }}
  .xref-link:hover {{ text-decoration: underline; }}

  /* ── TABS ── */
  .tab-bar {{
    display: flex; gap: 0; border-bottom: 1px solid var(--border);
    background: var(--surface); padding: 0 24px;
    position: sticky; top: 0; z-index: 100;
  }}
  .tab {{
    padding: 10px 20px; cursor: pointer; font-size: 12px; font-weight: 600;
    color: var(--text-muted); border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s; white-space: nowrap;
    user-select: none;
  }}
  .tab:hover {{ color: var(--text); }}
  .tab.active {{ color: var(--text); border-bottom-color: var(--accent); }}
  .tab-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; vertical-align: middle; }}

  /* ── PANELS ── */
  .panel {{ display: none; padding: 20px 24px 24px; }}
  .panel.active {{ display: block; }}

  /* ── PANEL HEADER ── */
  .panel-header {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;
  }}
  .panel-header h2 {{ font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 4px; }}
  .panel-header p  {{ font-size: 11px; color: var(--text-muted); }}

  /* ── LEGEND ── */
  .legend {{
    display: flex; flex-wrap: wrap; gap: 8px 20px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 16px; margin-bottom: 14px;
  }}
  .legend-title {{ width: 100%; font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }}
  .leg {{ display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-muted); }}
  .leg-swatch {{ width: 14px; height: 14px; border-radius: 3px; border: 1px solid rgba(255,255,255,0.15); flex-shrink: 0; }}
  .leg-line {{ width: 22px; height: 2px; border-radius: 1px; flex-shrink: 0; }}
  .leg-line.dashed {{ background: repeating-linear-gradient(90deg, currentColor 0, currentColor 4px, transparent 4px, transparent 8px); }}

  /* ── SVG CONTAINER ── */
  .svg-wrap {{
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: auto;
    max-height: 78vh;
    padding: 12px;
  }}
  .svg-wrap svg {{ display: block; }}

  /* ── DOT SOURCE ── */
  .dot-details {{
    margin-top: 14px;
  }}
  .dot-details summary {{
    cursor: pointer; font-size: 11px; color: var(--text-muted);
    padding: 6px 12px; background: var(--surface2);
    border: 1px solid var(--border); border-radius: 6px;
    user-select: none; list-style: none;
  }}
  .dot-details summary::-webkit-details-marker {{ display: none; }}
  .dot-details summary::before {{ content: "▶  "; font-size: 9px; }}
  .dot-details[open] summary::before {{ content: "▼  "; }}
  .dot-source {{
    margin-top: 6px; padding: 14px; background: var(--surface);
    border: 1px solid var(--border); border-radius: 6px;
    font-family: 'SF Mono', 'Cascadia Code', Consolas, monospace;
    font-size: 10px; color: #8b949e; white-space: pre; overflow-x: auto;
    max-height: 320px; overflow-y: auto;
  }}

  /* ── FOOTER ── */
  .page-footer {{
    border-top: 1px solid var(--border);
    padding: 12px 28px; margin-top: 10px;
    font-size: 10px; color: var(--text-muted);
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px;
  }}
</style>
</head>
<body>

<!-- ═══════════════════════════════ HEADER ═══════════════════════════════ -->
<div class="page-header">
  <h1>Lab Networking <span>ALPHA-002</span></h1>
  <div class="meta-row">
    <div class="meta-item"><strong>Project:</strong> My Local LAB (Mixed Arch k8s)</div>
    <div class="meta-item"><strong>Generated:</strong> {TODAY}</div>
    <div class="meta-item"><strong>Engine:</strong> Graphviz {pgv.__version__} via pygraphviz</div>
    <div class="meta-item"><strong>Ref:</strong> <a class="xref-link" href="lab_architecture-ALPHA-002.html">lab_architecture-ALPHA-002.html</a></div>
    <div class="meta-item"><span class="badge">3 diagrams embedded</span></div>
  </div>
</div>

<!-- ═══════════════════════════════ TAB BAR ══════════════════════════════ -->
<div class="tab-bar">
  <div class="tab active" onclick="showTab('logical', this)">
    <span class="tab-dot" style="background:#1f6feb"></span>Logical Topology
  </div>
  <div class="tab" onclick="showTab('vlan', this)">
    <span class="tab-dot" style="background:#79c0ff"></span>Physical / VLAN
  </div>
  <div class="tab" onclick="showTab('k8s', this)">
    <span class="tab-dot" style="background:#3fb950"></span>k3s Cluster &amp; SDN
  </div>
</div>

<!-- ═══════════════════════════════ PANEL 1 — LOGICAL ════════════════════ -->
<div id="panel-logical" class="panel active">
  <div class="panel-header">
    <h2>Logical Topology</h2>
    <p>Functional connectivity from WAN to services — compute clusters, storage fabric, identity chain, observability stack, and overlay networks.</p>
  </div>
  <div class="legend">
    <span class="legend-title">Colour key</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c2d48;border-color:#1f6feb"></span>Network / Infra</span>
    <span class="leg"><span class="leg-swatch" style="background:#122d1a;border-color:#3fb950"></span>ARM64 Compute</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c2a3d;border-color:#58a6ff"></span>x86-64 Compute</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c2030;border-color:#79c0ff"></span>Storage</span>
    <span class="leg"><span class="leg-swatch" style="background:#221733;border-color:#c8b1f5"></span>Identity / PKI</span>
    <span class="leg"><span class="leg-swatch" style="background:#2a1414;border-color:#ffa198"></span>Databases</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c2020;border-color:#39d353"></span>Observability</span>
    <span class="leg"><span class="leg-line" style="background:#3fb950"></span>ARM64 path</span>
    <span class="leg"><span class="leg-line" style="background:#79c0ff"></span>Storage path</span>
    <span class="leg"><span class="leg-line" style="background:#c8b1f5"></span>Identity / auth path</span>
    <span class="leg"><span class="leg-line dashed" style="color:#c8b1f5"></span>Dashed = overlay / SSO</span>
  </div>
  <div class="svg-wrap">{svg_logical}</div>
  <details class="dot-details">
    <summary>View Graphviz DOT source (logical_topology)</summary>
    <div class="dot-source">{LOGICAL_DOT.strip()}</div>
  </details>
</div>

<!-- ═══════════════════════════════ PANEL 2 — VLAN ══════════════════════ -->
<div id="panel-vlan" class="panel">
  <div class="panel-header">
    <h2>Physical / VLAN Map</h2>
    <p>Nodes grouped by VLAN membership with management IPs. Includes TB4 mesh backbone, Tailscale overlay, storage fabric paths, and vMotion connectivity.</p>
  </div>
  <div class="legend">
    <span class="legend-title">VLAN colour key</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c1830;border-color:#1f6feb"></span>VLAN 10 — Mgmt  10.10.10.0/24</span>
    <span class="leg"><span class="leg-swatch" style="background:#0d1f10;border-color:#3fb950"></span>VLAN 20 — VM LAN  10.10.20.0/24</span>
    <span class="leg"><span class="leg-swatch" style="background:#0d1b2a;border-color:#79c0ff"></span>VLAN 30 — Storage  10.10.30.0/24  MTU 9000</span>
    <span class="leg"><span class="leg-swatch" style="background:#1f1a0d;border-color:#e3b341"></span>VLAN 40 — vMotion  10.10.40.0/24  MTU 9000</span>
    <span class="leg"><span class="leg-swatch" style="background:#1f0d0d;border-color:#f85149"></span>VLAN 50 — DMZ  10.10.50.0/24 (reserved)</span>
    <span class="leg"><span class="leg-swatch" style="background:#0a1a0a;border-color:#3fb950"></span>TB4 Mesh  192.168.100.0/24  40 Gb/s</span>
    <span class="leg"><span class="leg-swatch" style="background:#1c1429;border-color:#c8b1f5"></span>Tailscale  100.64.0.0/10</span>
  </div>
  <div class="svg-wrap">{svg_vlan}</div>
  <details class="dot-details">
    <summary>View Graphviz DOT source (physical_vlan)</summary>
    <div class="dot-source">{VLAN_DOT.strip()}</div>
  </details>
</div>

<!-- ═══════════════════════════════ PANEL 3 — k8s ════════════════════════ -->
<div id="panel-k8s" class="panel">
  <div class="panel-header">
    <h2>k3s Cluster — SDN &amp; Node / Workload View</h2>
    <p>k3s control plane and worker nodes, Flannel VXLAN overlay, Thunderbolt 4 mesh backbone, Storage Class bindings, CoreDNS→FreeIPA chain, and pinned workloads per node.</p>
  </div>
  <div class="legend">
    <span class="legend-title">Cluster legend</span>
    <span class="leg"><span class="leg-swatch" style="background:#122d1a;border-color:#3fb950"></span>ARM64 nodes (mm-cp, mm-w1, mm-w2)</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c2a3d;border-color:#58a6ff"></span>AMD64 nodes (x86-w1, x86-w2)  taint: arch=amd64:NoSchedule</span>
    <span class="leg"><span class="leg-swatch" style="background:#1c1a2d;border-color:#c8b1f5"></span>SDN Overlay (Flannel VXLAN  10.42/16  ·  svc 10.43/16)</span>
    <span class="leg"><span class="leg-swatch" style="background:#0c2030;border-color:#79c0ff"></span>Storage Classes → NFS / iSCSI / Ceph</span>
    <span class="leg"><span class="leg-line" style="background:#3fb950;height:3px;border-radius:2px"></span>TB4 mesh (40 Gb/s, bold)</span>
    <span class="leg"><span class="leg-line dashed" style="color:#c8b1f5"></span>Dashed = Flannel / DNS / auth overlay</span>
    <span class="leg"><span class="leg-line dashed" style="color:#79c0ff"></span>Dashed = PVC binding to storage class</span>
  </div>
  <div class="svg-wrap">{svg_k8s}</div>
  <details class="dot-details">
    <summary>View Graphviz DOT source (k8s_cluster)</summary>
    <div class="dot-source">{K8S_DOT.strip()}</div>
  </details>
</div>

<!-- ═══════════════════════════════ FOOTER ═══════════════════════════════ -->
<div class="page-footer">
  <span>lab_networking-ALPHA-002.html  ·  My Local LAB (Mixed Arch k8s)  ·  {TODAY}</span>
  <span>Graphviz {pgv.__version__}  ·  DOT sources embedded in &lt;details&gt; blocks above  ·  Ref: <a class="xref-link" href="lab_architecture-ALPHA-002.html">lab_architecture-ALPHA-002.html</a></span>
</div>

<!-- ═══════════════════════════════ TAB JS ═══════════════════════════════ -->
<script>
function showTab(name, el) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  el.classList.add('active');
}}
</script>

</body>
</html>"""

out_path = "/home/ubuntu/lab_networking-ALPHA-002.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"\nWrote: {out_path}  ({len(HTML):,} bytes)")
