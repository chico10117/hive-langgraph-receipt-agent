# Hive LangGraph Receipt Agent

Minimal LangGraph agent for the Hive Embed Bounty. It invokes a deterministic
LangChain fake LLM inside a LangGraph state machine and mints a Hive receipt
through the official `langchain-hive` callback.

The receipt payload is privacy-preserving: the callback sends hashes and run
metadata, not the raw prompt or output.

## One-command Run

```sh
./run.sh
```

The command creates a local virtual environment, installs dependencies, runs the
agent once, verifies the minted receipt exists, and prints a
`https://thehiveryiq.com/verify/?id=...` URL.

## Bounty Metadata

- Framework: LangGraph
- Hive SDK: `langchain-hive`
- License: MIT
- Payout wallet: `0xb19262185bac9748e2b71674Ef48676448F7A516` on Base 8453
- Referrer tag: loaded from `hive_referrer_code.txt` or `HIVE_REFERRER_CODE`

## Manual Run

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python agent.py
```

