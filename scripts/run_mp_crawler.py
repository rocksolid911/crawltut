#!/usr/bin/env python3
"""
Script to run the Member of Parliament (MP) crawler.

Usage:
    python scripts/run_mp_crawler.py --year 2024
    python scripts/run_mp_crawler.py --years 2024 2019 2014
    python scripts/run_mp_crawler.py --year 2024 --winners-only
    python scripts/run_mp_crawler.py --year 2024 --force-regenerate
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crawlers.mp_crawler import run_mp_crawler_for_years


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run the Member of Parliament (MP) crawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl 2024 election data (all candidates)
  python scripts/run_mp_crawler.py --year 2024

  # Crawl multiple years
  python scripts/run_mp_crawler.py --years 2024 2019 2014

  # Crawl only winners
  python scripts/run_mp_crawler.py --year 2024 --winners-only

  # Force regenerate JSON files
  python scripts/run_mp_crawler.py --year 2024 --force-regenerate

  # Crawl all available years (2004-2024)
  python scripts/run_mp_crawler.py --all-years
        """
    )

    year_group = parser.add_mutually_exclusive_group(required=True)
    year_group.add_argument(
        '--year',
        type=int,
        help='Single election year to process'
    )
    year_group.add_argument(
        '--years',
        type=int,
        nargs='+',
        help='Multiple election years to process'
    )
    year_group.add_argument(
        '--all-years',
        action='store_true',
        help='Process all available years (2004, 2009, 2014, 2019, 2024)'
    )

    parser.add_argument(
        '--winners-only',
        action='store_true',
        help='Only process election winners'
    )
    parser.add_argument(
        '--force-regenerate',
        action='store_true',
        help='Force regenerate JSON files even if they exist'
    )
    parser.add_argument(
        '--no-skip-force-regenerated',
        action='store_true',
        help='Do not skip candidates that were already force-regenerated'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Determine which years to process
    if args.year:
        years = [args.year]
    elif args.years:
        years = args.years
    elif args.all_years:
        years = [2024, 2019, 2014, 2009, 2004]
    else:
        print("Error: Must specify --year, --years, or --all-years")
        sys.exit(1)

    # Print configuration
    print("=" * 80)
    print("MP Crawler Configuration")
    print("=" * 80)
    print(f"Years to process: {years}")
    print(f"Winners only: {args.winners_only}")
    print(f"Force regenerate: {args.force_regenerate}")
    print(f"Skip force-regenerated: {not args.no_skip_force_regenerated}")
    print("=" * 80)
    print()

    # Run the crawler
    try:
        asyncio.run(
            run_mp_crawler_for_years(
                years=years,
                winners_only=args.winners_only,
                force_regenerate_json=args.force_regenerate,
                skip_if_force_regenerated=not args.no_skip_force_regenerated
            )
        )
        print("\n" + "=" * 80)
        print("MP Crawler completed successfully!")
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
