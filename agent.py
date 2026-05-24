#!/usr/bin/env python3
"""Run a deterministic LangGraph agent and mint a Hive receipt."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, TypedDict

import httpx
from langchain_core.language_models.fake import FakeListLLM
from langchain_hive import HiveCallbackHandler
from langgraph.graph import END, StateGraph


ROOT = Path(__file__).resolve().parent
TARGET_WALLET = "0x820a7bf90d944bb26bfD9b62Ab172Fc3A0829cB9"


class AgentState(TypedDict):
    prompt: str
    answer: str
    verify_url: str


class RecordingHiveCallbackHandler(HiveCallbackHandler):
    """Hive callback that records the receipt ID while preserving SDK metadata."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.receipts: list[dict[str, Any]] = []
        self.done = threading.Event()
        self.error: str | None = None

    def _post(self, body: dict[str, Any]) -> None:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.endpoint, json=body, headers=headers)
            response.raise_for_status()
            envelope = response.json()
            receipt_id = envelope.get("receipt_id") or envelope.get("id")
            if not receipt_id:
                raise RuntimeError(f"Hive response did not include a receipt id: {envelope}")
            self.receipts.append(
                {
                    "receipt_id": receipt_id,
                    "verify_url": f"https://thehiveryiq.com/verify/?id={receipt_id}",
                    "raw_response": envelope,
                }
            )
        except Exception as exc:  # pragma: no cover - surfaced by main wait.
            self.error = str(exc)
        finally:
            self.done.set()


def load_referrer_code() -> str:
    env_code = os.environ.get("HIVE_REFERRER_CODE", "").strip()
    if env_code:
        return env_code

    code_file = ROOT / "hive_referrer_code.txt"
    if code_file.exists():
        file_code = code_file.read_text(encoding="utf-8").strip()
        if file_code:
            return file_code

    return "bounty_pending"


def llm_node(state: AgentState, hive: RecordingHiveCallbackHandler) -> AgentState:
    llm = FakeListLLM(
        responses=[
            "Hive receipt agent completed a deterministic LangGraph run for Base USDC bounty verification."
        ],
        callbacks=[hive],
    )
    answer = llm.invoke(state["prompt"])
    return {**state, "answer": answer}


def build_graph(hive: RecordingHiveCallbackHandler):
    graph = StateGraph(AgentState)
    graph.add_node("llm_receipt_step", lambda state: llm_node(state, hive))
    graph.set_entry_point("llm_receipt_step")
    graph.add_edge("llm_receipt_step", END)
    return graph.compile()


def verify_receipt(receipt_id: str) -> dict[str, Any]:
    url = f"https://hivemorph.onrender.com/v1/receipt/{receipt_id}"
    response = httpx.get(url, timeout=8)
    response.raise_for_status()
    return response.json()


def main() -> None:
    tag = load_referrer_code()
    hive = RecordingHiveCallbackHandler(tag=tag, timeout=8)
    graph = build_graph(hive)

    result = graph.invoke(
        {
            "prompt": (
                "Run a deterministic receipt-minting step for a LangGraph bounty "
                f"submission paying Base USDC to {TARGET_WALLET}."
            ),
            "answer": "",
            "verify_url": "",
        }
    )

    if not hive.done.wait(timeout=12):
        raise TimeoutError("Timed out waiting for Hive receipt mint")
    if hive.error:
        raise RuntimeError(f"Hive receipt mint failed: {hive.error}")
    if not hive.receipts:
        raise RuntimeError("Hive callback completed without a recorded receipt")

    receipt = hive.receipts[-1]
    receipt_id = receipt["receipt_id"]
    receipt["receipt_lookup"] = verify_receipt(receipt_id)
    receipt["answer"] = result["answer"]
    receipt["tag"] = tag
    receipt["framework"] = "langgraph"
    receipt["payout_wallet"] = TARGET_WALLET

    (ROOT / "latest_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(receipt["verify_url"])


if __name__ == "__main__":
    main()
