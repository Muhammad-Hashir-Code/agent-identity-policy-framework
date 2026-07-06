<div align="center">

# 🛡️ Agent Identity & Policy Framework (AIPF)

### A Cryptographic Reference Architecture for Autonomous Agent Identity & Runtime Policy Enforcement

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Protocol](https://img.shields.io/badge/AIPF--protocol-1.0.0-8A2BE2.svg)]()
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-2ea44f.svg)](https://modelcontextprotocol.io)
[![Status](https://img.shields.io/badge/status-research%20prototype-orange.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)

*Closing the "identity deficit" between autonomous LLM agents and legacy web security primitives.*

[Overview](#-executive-summary) •
[Architecture](#️-system-architecture) •
[Threat Model](#️-cryptographic-threat-mitigation) •
[Benchmarks](#-empirical-benchmarking--performance) •
[Setup](#-installation--setup) •
[MCP Integration](#-model-context-protocol-mcp-integration) •
[Roadmap](#-future-research-pathways-fellowship-agenda)

</div>

<br>

## 📖 Executive Summary

The rapid transition from passive Large Language Models (LLMs) to autonomous, stateful agents capable of multi-step tool execution has outpaced web security infrastructure. Legacy identity primitives (TLS, OAuth 2.0, API keys) authenticate host endpoints or human principals, but they fail to capture an agent's internal composition, model family, or delegated operational boundaries. This is the **identity deficit**.

The **Agent Identity & Policy Framework (AIPF)** is a modular, multi-layer reference architecture that resolves this vulnerability. It cleanly separates global interoperability claims from local sovereign security rules.

> [!IMPORTANT]
> AIPF does not replace current transport protocols. Instead, it **layers on top of them** (such as the Model Context Protocol or TLS), introducing cryptographic proof of model identity and explicit runtime safety bounds.

<br>

## ⚙️ System Architecture

```
               ┌─────────────────────────────────────────────┐
               │      Agent Identity Assertion (AIA)          │
               │  • Globally verifiable cryptographic token   │
               │  • Identifies: Model family, Principal       │
               └─────────────────────────────────────────────┘
                                     │
                       Linked via Cryptographic Binding
                                     ▼
               ┌─────────────────────────────────────────────┐
               │  Agent Capability & Policy Descriptor (ACPD) │
               │  • Session-specific scoped permissions       │
               │  • Cryptographically bound to AIA hash        │
               └─────────────────────────────────────────────┘
                                     │
                           Validated locally by
                                     ▼
               ┌─────────────────────────────────────────────┐
               │     Local Enforcement Interface (LEI)        │
               │  • Independent verification of signatures     │
               │  • Localized policy application (low latency) │
               └─────────────────────────────────────────────┘
```

### ⚡ Key Architectural Layers

AIPF divides security concerns into three logical layers, ensuring that security scales without sacrificing performance or imposing centralized trust gatekeepers.

<table>
<tr>
<td width="90"><b>Layer 1</b></td>
<td>

**Agent Identity Assertion (AIA)**
Portable, cryptographically signed assertions that bind an active agent instance to its underlying model composition (e.g., `llama-3-70b-instruct`) and its legally accountable principal.

</td>
</tr>
<tr>
<td><b>Layer 2</b></td>
<td>

**Agent Capability & Policy Descriptor (ACPD)**
A session-scoped, dynamic descriptor containing the agent's current allowed permissions, constraints (e.g., maximum dollar value of transactions), and nonces. To mitigate interception and forgery, the ACPD is cryptographically bound to the AIA using a secure hashing mechanism.

</td>
</tr>
<tr>
<td><b>Layer 3</b></td>
<td>

**Local Enforcement Interface (LEI)**
A lightweight, sovereign runtime interface deployed on the relying party's infrastructure. The LEI verifies both the AIA and ACPD signatures, validates the session binding, and applies local policies (e.g., rate limits, manual human escalation triggers) with minimal overhead.

</td>
</tr>
</table>

<br>

## 🛡️ Cryptographic Threat Mitigation

AIPF is designed to resist standard network threats as well as vulnerabilities unique to autonomous systems. Under a **Dolev-Yao-style adversary** (capable of eavesdropping, intercepting, and modifying messages but unable to break cryptographic primitives), AIPF enforces rigorous safety guarantees:

| Threat Category | Attack Vector | AIPF Technical Mitigation |
|---|---|---|
| 🧨 **Tampering** | Intercepting a valid ACPD and elevating its permission scopes. | 🔒 **Layer 2 Signatures** — any tampering invalidates the signature generated by the operator's private key. |
| ♻️ **Replay / Spoofing** | Reusing old identity credentials or captured session descriptors on a separate endpoint. | 🔗 **Cryptographic Session Binding** — the ACPD contains a secure SHA-256 binding hash (`H_binding = Hash(AIA)`). Reusing the ACPD with a different AIA, or vice versa, causes a cryptographic mismatch in the LEI. |
| 🎭 **Confused Deputy** | Trick a privileged agent into executing unauthorized tool calls. | 🛑 **Explicit Scope Enforcement** — the LEI compares every action to the explicit permissions listed in the signed ACPD, rejecting unauthorized calls at the system boundary before model execution occurs. |

<br>

## 📊 Empirical Benchmarking & Performance

To address concerns over cryptographic latency overhead in high-throughput agent deployments, this prototype includes an automated benchmarking suite.

The suite generates 2048-bit RSA keypairs, signs the AIA, generates the ACPD with a SHA-256 binding hash, and runs complete verification checks at the LEI over a 100-iteration sequence.

### Performance Results

| Metric | Value |
|---|---|
| ⏱️ Average processing latency | **≈ 1.4 ms** per verification handshake |
| 🧠 Typical LLM inference cycle | 500 ms – 2000 ms |
| 📉 Overhead as % of execution time | **< 0.3%** |

**Feasibility Analysis:** Since typical LLM inference cycles range from 500 ms to 2000 ms, AIPF's verification overhead is practically negligible (**< 0.3%** of overall execution time). This makes it highly viable for real-time, high-frequency tool-calling sequences.

> [!NOTE]
> Latency tests were run locally using 2048-bit RSA key configurations. Utilizing alternative, lighter elliptic curve cryptography (such as **Ed25519**) can reduce processing times even further.

<br>

## 📦 Installation & Setup

> [!TIP]
> Ensure you have **Python 3.8+** installed before proceeding.

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/aipf-prototype.git
cd aipf-prototype
```

**2. Install cryptographic dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the benchmark & verification script**

```bash
python aipf_poc.py
```

<br>

## 🌐 Model Context Protocol (MCP) Integration

AIPF does not require a protocol redesign; it layers directly over industry-standard transport mechanisms.

To demonstrate how these assertions travel over real systems, [`examples/mcp_initialize_request.json`](examples/mcp_initialize_request.json) contains a standard-compliant Model Context Protocol (MCP) initialization envelope. The AIA and ACPD payloads are seamlessly mapped inside a custom `authentication` parameter:

<details>
<summary><b>📄 Click to expand: Sample MCP Initialization Envelope</b></summary>

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "clientInfo": {
      "name": "AIPF-Enabled-Agent-Client",
      "version": "1.0.0"
    },
    "authentication": {
      "aipf_protocol_version": "1.0.0",
      "aia": {
        "payload": {
          "agent_id": "did:example:agent-007",
          "principal": "did:example:hashir-labs",
          "composition": {
            "model_family": "llama-3-70b-instruct",
            "certification_hash": "a1b2c3d4..."
          },
          "issuer": "Global_CUNY_Trust",
          "issued_at": 1719876543,
          "expires_at": 1719880143
        },
        "signature_b64": "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQ..."
      },
      "acpd": {
        "payload": {
          "aia_binding_hash": "cf23df2207d99a74fbe169e3eba035e633b65d94",
          "scopes": ["read_db", "api_call"],
          "nonce": "server-challenge-nonce-98213",
          "issued_at": 1719876545
        },
        "signature_b64": "GgSCDKgDQEFAASCBKgwggSkAgEAAoIBAQ..."
      }
    }
  }
}
```

</details>

<br>

## 🔬 Future Research Pathways (Fellowship Agenda)

This prototype acts as the foundational technical baseline. During the **Singapore AI Safety Fellowship**, the research will expand to investigate:

- [ ] **Privacy-Preserving Attestations** — utilizing BBS+ signatures or Zero-Knowledge Proofs (ZKPs) so agents can verify model alignment parameters without leaking corporate principal identities.
- [ ] **Socio-Technical Governance** — designing federated trust registry incentive structures and mapping audit trails to compliance frameworks like the **EU AI Act**.

<br>

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the issues page or open a pull request.

<br>

## 📄 License

This repository is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

<br>

<div align="center">


</div>
