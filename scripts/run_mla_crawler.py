#!/usr/bin/env python3
"""
Script to run the Member of Legislative Assembly (MLA) crawler.

Usage:
    python scripts/run_mla_crawler.py --all-states
    python scripts/run_mla_crawler.py --state "Maharashtra"
    python scripts/run_mla_crawler.py --states "Maharashtra" "Karnataka" "Tamil Nadu"
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crawlers.mla_crawler import run_mla_crawler
from config.settings import INDIAN_STATES


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run the Member of Legislative Assembly (MLA) crawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl all states
  python scripts/run_mla_crawler.py --all-states

  # Crawl a single state
  python scripts/run_mla_crawler.py --state "Maharashtra"

  # Crawl multiple states
  python scripts/run_mla_crawler.py --states "Maharashtra" "Karnataka" "Tamil Nadu"

Available states:
  """ + "\n  ".join(INDIAN_STATES)
    )

    state_group = parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument(
        '--state',
        type=str,
        help='Single state to process'
    )
    state_group.add_argument(
        '--states',
        type=str,
        nargs='+',
        help='Multiple states to process'
    )
    state_group.add_argument(
        '--all-states',
        action='store_true',
        help='Process all available states'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='state_assembly',
        help='Output directory for state assembly data (default: state_assembly)'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Determine which states to process
    if args.state:
        states = [args.state]
    elif args.states:
        states = args.states
    elif args.all_states:
        states = None  # None means all states
    else:
        print("Error: Must specify --state, --states, or --all-states")
        sys.exit(1)

    # Validate state names
    if states:
        invalid_states = [s for s in states if s not in INDIAN_STATES]
        if invalid_states:
            print(f"Error: Invalid state names: {invalid_states}")
            print(f"\nAvailable states:")
            for state in INDIAN_STATES:
                print(f"  - {state}")
            sys.exit(1)

    # Print configuration
    print("=" * 80)
    print("MLA Crawler Configuration")
    print("=" * 80)
    if states:
        print(f"States to process: {states}")
    else:
        print(f"States to process: All {len(INDIAN_STATES)} states")
    print(f"Output directory: {args.output_dir}")
    print("=" * 80)
    print()

    # Run the crawler
    try:
        asyncio.run(run_mla_crawler(states=states))
        print("\n" + "=" * 80)
        print("MLA Crawler completed successfully!")
        print("=" * 80)
    except KeyboardInterrupt:
        print("\n\nCrawler interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running crawler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
