<div align="center">

#  SlopCheck-CLI

### *Zero GPU. Zero API keys. Zero mercy for "delving into a multifaceted journey."*

[![PyPI](https://img.shields.io/badge/pip%20install-slopcheck-blue?style=flat-square)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](#)
[![Python](https://img.shields.io/badge/python-3.10%2B-yellow?style=flat-square)](#)
[![Deps](https://img.shields.io/badge/dependencies-0-brightgreen?style=flat-square)](#)
[![Status](https://img.shields.io/badge/status-v0.1.0%20stable-success?style=flat-square)](#)

</div>

---

##  What is this thing?

Your writing sounds like it was "delving" into a "tapestry" of "multifaceted" ideas and "testament"-ing its way to a conclusion? **SlopCheck knows.**

It's a fully offline, zero-dependency AI-prose detector that reads your text the way a tired English teacher reads a suspicious essay, then hands back a cold, hard score.

No GPU. No API key. No cloud. No excuses.

##  Why developers actually like it

|  The Old Way |  The SlopCheck Way |
|---|---|
| Pay for a cloud "AI detector" | Runs 100% on your CPU, offline |
| Wait on network round-trips | Instant, local, stdlib-only |
| Black-box "trust me" score | 5 transparent heuristic signals |
| Manual review before merge | Drop it in your CI, block the slop |

##  Get it running (30 seconds, we timed it)

```bash
pip install slopcheck-cli
```

Point it at a file:

```bash
slopcheck doc.txt --explain
```

Or pipe anything into its mouth:

```bash
echo "delving into multifaceted layers" | slopcheck -
```

###  Sample verdict

```
slopcheck: stdin
Score: 45/100  (medium AI-signal density)

Phrase matches         5/40
Sentence rhythm        15/20
Punctuation             10/15
Paragraph uniformity   10/15
Lexical diversity        5/10

Flagged spans:
  L1: "...delving into this multifaceted ecosystem..."

  Heuristic estimate, not proof. False positives happen
    on formal/corporate writing and non-native English styles.
```

##  How Sniffy actually smells the slop

Five independent signals, no ML, no black box:

- **📖 Phrase matcher**: greedy scan against a weighted bank of known AI clichés
- **🎵 Sentence rhythm**: flags suspiciously *uniform* sentence lengths (real humans ramble)
- **✒️ Punctuation signature**: em-dash, colon, and parenthesis frequency checked against a bot-like baseline
- **📐 Paragraph uniformity**: every paragraph exactly the same size? Suspicious.
- **🔤 Lexical diversity**: Type-Token Ratio checks if your vocabulary is actually alive

##  CLI cheat sheet

```bash
slopcheck <file|->     # target file, or "-" for stdin
  --json                # machine-readable output
  --explain              # show flagged spans + context
  --no-color              # for your soulless CI logs
```

##  Use it as a library too

```python
from slopcheck import scorer

result = scorer.score("Text to evaluate")
print(result.score, result.signals)
```

##  CI gatekeeper mode

SlopCheck exits with code `1` on high-risk documents, so wire it straight into pre-commit or CI and let Sniffy guard the gate.

```yaml
- name: Block the slop
  run: slopcheck docs/*.md --no-color
```

##  Under the hood

```
slopcheck/
├── cli.py            → argument parsing & runner
├── scorer.py          → orchestrates all 5 signals
├── render.py           → console + JSON formatting
├── signals/
│   ├── phrases.py        → AI-cliché matcher
│   ├── rhythm.py           → sentence-length variance
│   ├── punctuation.py       → em-dash / colon frequency
│   ├── structure.py          → paragraph uniformity
│   └── lexical.py             → TTR vocabulary scorer
└── data/phrase_bank.json    → the naughty-phrase database
```

##  Contributing

Found new slop in the wild? Sniffy accepts submissions. See `CONTRIBUTING.md`.

##  License

MIT: free as in "delving into the multifaceted world of open source."

---

<div align="center">

**SlopCheck** · *sniffing out the tapestry, one testament at a time* 🐾

</div>
