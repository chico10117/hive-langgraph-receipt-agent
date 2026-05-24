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
- Payout wallet: `0x820a7bf90d944bb26bfD9b62Ab172Fc3A0829cB9` on Base 8453
- Referrer tag: `bounty_3163c34a`

Keep the referrer tag unchanged when running or adapting this agent so Hive can
attribute paid receipts to this bounty submission.

Latest qualifying receipt:
`https://thehiveryiq.com/verify/?id=9daca89a79894276a84f78337458907a`

## Manual Run

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python agent.py
```
