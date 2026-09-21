#!/usr/bin/env python3
"""Diagnostic script for Comelit ICONA Bridge.

Connects to a 6722W (or other ICONA Bridge device), authenticates,
and dumps the full configuration including discovered entrance panels,
doors, actuators, and server info.

Usage:
    python3 scripts/diagnose.py <HOST> [--token TOKEN] [--password PASSWORD]

If no token is given, attempts auto-extraction from a device backup.
"""

import argparse
import asyncio
import json
import sys
import os

# Add the custom_components path so we can import the integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from custom_components.comelit_intercom.comelit_client import IconaBridgeClient


async def run(host: str, port: int, token: str | None, password: str) -> None:
    """Connect, authenticate, and dump device config."""
    client = IconaBridgeClient(host, port)

    # --- resolve token if not provided ---
    if not token:
        print(f"\nNo token provided — attempting extraction from device backup...")
        try:
            from custom_components.comelit_intercom.token_extractor import extract_token
            token = await extract_token(host, password=password)
            if token:
                print(f"  Extracted token: {token[:8]}...{token[-4:]}")
            else:
                print("  FAILED: Could not extract token from backup.")
                print("  Check the web password (default: 'comelit') or provide --token.")
                return
        except Exception as e:
            print(f"  FAILED: {e}")
            print("  Install aiohttp (pip install aiohttp) or provide --token.")
            return

    # --- connect ---
    print(f"\nConnecting to {host}:{port}...")
    try:
        await client.connect()
        print("  Connected OK")
    except Exception as e:
        print(f"  FAILED: {e}")
        return

    try:
        # --- authenticate ---
        print(f"\nAuthenticating (token: {token[:8]}...)...")
        auth_code = await client.authenticate(token)
        if auth_code == 200:
            print("  Auth OK (code 200)")
        else:
            print(f"  FAILED: code {auth_code}")
            if auth_code == 403:
                print("  Token is invalid or expired. Re-provision or extract a new one.")
            return

        # --- server info ---
        print("\n--- SERVER INFO ---")
        try:
            info = await client.get_server_info()
            if info:
                model_map = {"MnWi": "6742W Mini ViP", "MSVF": "6741W Mini ViP"}
                model_code = info.get("model", "unknown")
                print(f"  Model:    {model_code} ({model_map.get(model_code, 'unknown product')})")
                print(f"  Firmware: {info.get('version', 'unknown')}")
                print(f"  Serial:   {info.get('serial-code', 'unknown')}")
                print(f"  Raw:      {json.dumps(info, indent=2)}")
            else:
                print("  (no server-info response)")
        except Exception as e:
            print(f"  (server-info failed: {e})")

        # --- full config ---
        print("\n--- CONFIGURATION ---")
        config = await client.get_config("all")
        if not config:
            print("  FAILED: no config response")
            return

        if "vip" not in config:
            print("  WARNING: no 'vip' key in config — this device may not support VIP")
            print(f"  Config keys: {list(config.keys())}")
            print(f"  Raw config:\n{json.dumps(config, indent=2)}")
            return

        vip = config["vip"]
        user_params = vip.get("user-parameters", {})

        # Apartment address
        print(f"\n  Apartment address: {vip.get('apt-address', '?')}")
        print(f"  Apartment sub:     {vip.get('apt-subaddress', '?')}")

        # Entrance panels (4899 units should appear here)
        entrances = user_params.get("entrance-address-book", [])
        print(f"\n--- ENTRANCE PANELS ({len(entrances)}) ---")
        print("  These are your external units (e.g. 4899 Quadra) with cameras.")
        if entrances:
            for i, ent in enumerate(entrances):
                print(f"\n  [{i}] {ent.get('name', 'Unnamed')}")
                print(f"      apt-address:  {ent.get('apt-address', '?')}")
                print(f"      output-index: {ent.get('output-index', '?')}")
                for k, v in ent.items():
                    if k not in ("name", "apt-address", "output-index"):
                        print(f"      {k}: {v}")
        else:
            print("  (none found)")

        # Doors
        doors = user_params.get("opendoor-address-book", [])
        print(f"\n--- DOORS ({len(doors)}) ---")
        print("  These become lock entities you can open.")
        if doors:
            for i, door in enumerate(doors):
                print(f"\n  [{i}] {door.get('name', 'Unnamed')}")
                print(f"      apt-address:  {door.get('apt-address', '?')}")
                print(f"      output-index: {door.get('output-index', '?')}")
                for k, v in door.items():
                    if k not in ("name", "apt-address", "output-index"):
                        print(f"      {k}: {v}")
        else:
            print("  (none found)")

        # Actuators
        actuators = user_params.get("actuator-address-book", [])
        print(f"\n--- ACTUATORS ({len(actuators)}) ---")
        print("  Gates, barriers, and other relay-controlled devices.")
        if actuators:
            for i, act in enumerate(actuators):
                print(f"\n  [{i}] {act.get('name', 'Unnamed')}")
                print(f"      apt-address:  {act.get('apt-address', '?')}")
                print(f"      output-index: {act.get('output-index', '?')}")
                for k, v in act.items():
                    if k not in ("name", "apt-address", "output-index"):
                        print(f"      {k}: {v}")
        else:
            print("  (none found)")

        # Opendoor actions (peer/TAP for 1456S gateways)
        actions = user_params.get("opendoor-actions", [])
        if actions:
            print(f"\n--- OPENDOOR ACTIONS ({len(actions)}) ---")
            for i, act in enumerate(actions):
                print(f"  [{i}] {json.dumps(act)}")

        # Other address books
        other_books = {
            k: v for k, v in user_params.items()
            if k.endswith("-address-book")
            and k not in ("opendoor-address-book", "entrance-address-book", "actuator-address-book")
        }
        if other_books:
            print(f"\n--- OTHER ADDRESS BOOKS ---")
            for book_name, entries in other_books.items():
                print(f"\n  {book_name} ({len(entries)} entries):")
                for i, entry in enumerate(entries):
                    print(f"    [{i}] {json.dumps(entry)}")

        # Full raw dump
        print(f"\n--- FULL RAW VIP CONFIG ---")
        print(json.dumps(vip, indent=2))

    finally:
        await client.shutdown()
        print("\nDone.")


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose a Comelit ICONA Bridge device"
    )
    parser.add_argument("host", help="IP address of the 6722W indoor monitor")
    parser.add_argument("--port", type=int, default=64100, help="ICONA Bridge port (default: 64100)")
    parser.add_argument("--token", help="32-char hex auth token (auto-extracted if omitted)")
    parser.add_argument("--password", default="comelit", help="Web UI password (default: comelit)")
    args = parser.parse_args()

    asyncio.run(run(args.host, args.port, args.token, args.password))


if __name__ == "__main__":
    main()
