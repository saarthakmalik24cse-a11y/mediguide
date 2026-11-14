"""Read-only demo preflight. Run after seed_data.py, before the presentation."""
import sys
from mediguide.release import VERSION, readiness


def main():
    print(f"MediGuide {VERSION} | local educational demo")
    checks = readiness()
    for item in checks:
        print(f"{'READY' if item['ready'] else 'MISSING/INVALID'}: {item['module']} "
              f"({item.get('sources', 0)} sources, {item.get('chunks', 0)} chunks)")
    if not all(item["ready"] for item in checks):
        print("Run seed_data.py for demo data. Back up user indexes before repairing them.")
        return 1
    print("Demo indexes ready. This is not a medical/security certification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
