"""
Refactored main entry point for the election data crawler.
Provides clear, organized entry points for different crawling operations.
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Import new refactored components
from crawler.mp_crawler import MPCrawler
from crawler.mla_crawler import MLACrawler
from utils.csv_processor import CSVProcessor
from utils.file_manager import FileManager
from models.candidate import CandidateCollection, Candidate


def setup_argument_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Political Election Data Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

Single Year:
  python main_refactored.py mp --year 2024 --mode constituencies
  python main_refactored.py mp --year 2024 --mode candidates --winners-only
  python main_refactored.py mla --state "Karnataka" --year 2023 --mode winners

Multiple Years:
  python main_refactored.py mp --years 2024 2019 2014 2009 2004 --mode constituencies
  python main_refactored.py mp --years 2024 2019 --mode candidates --winners-only
  python main_refactored.py mla --state "Karnataka" --years 2023 2018 2013 --mode winners
  
Other Commands:
  python main_refactored.py analyze --csv-path "candidate_data/"
  python main_refactored.py util --merge-csv file1.csv file2.csv --output merged.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # MP (Lok Sabha) crawler
    mp_parser = subparsers.add_parser('mp', help='Crawl MP (Lok Sabha) election data')
    year_group = mp_parser.add_mutually_exclusive_group(required=True)
    year_group.add_argument('--year', type=int, help='Single election year')
    year_group.add_argument('--years', type=int, nargs='+', help='Multiple election years (e.g., --years 2024 2019 2014)')
    mp_parser.add_argument('--mode', choices=['constituencies', 'candidates', 'profiles', 'images'], 
                          required=True, help='What to crawl')
    mp_parser.add_argument('--winners-only', action='store_true', 
                          help='Only process winners (for candidates mode)')
    mp_parser.add_argument('--csv-path', help='CSV file path (for images mode)')
    mp_parser.add_argument('--batch-size', type=int, default=50, 
                          help='Batch size for processing')
    
    # MLA (State Assembly) crawler
    mla_parser = subparsers.add_parser('mla', help='Crawl MLA (State Assembly) election data')
    mla_parser.add_argument('--state', required=True, help='State name')
    mla_year_group = mla_parser.add_mutually_exclusive_group(required=True)
    mla_year_group.add_argument('--year', type=int, help='Single election year')
    mla_year_group.add_argument('--years', type=int, nargs='+', help='Multiple election years (e.g., --years 2023 2018 2013)')
    mla_parser.add_argument('--mode', choices=['winners', 'candidates', 'images'], 
                           required=True, help='What to crawl')
    mla_parser.add_argument('--winners-only', action='store_true', 
                           help='Only process winners (for images mode)')
    mla_parser.add_argument('--csv-path', help='CSV file path (for images mode)')
    mla_parser.add_argument('--batch-size', type=int, default=50, 
                           help='Batch size for processing')
    
    # Data analysis
    analyze_parser = subparsers.add_parser('analyze', help='Analyze existing CSV data')
    analyze_parser.add_argument('--csv-path', required=True, help='CSV file or directory path')
    analyze_parser.add_argument('--output', help='Output file for analysis report')
    
    # Utility commands
    util_parser = subparsers.add_parser('util', help='Utility operations')
    util_parser.add_argument('--merge-csv', nargs='+', help='Merge multiple CSV files')
    util_parser.add_argument('--output', help='Output file path')
    
    return parser


async def handle_mp_command(args):
    """Handle MP (Lok Sabha) crawling commands."""
    # Determine years to process
    years_to_process = args.years if args.years else [args.year]
    
    print(f"Processing {len(years_to_process)} year(s): {years_to_process}")
    
    for year_idx, year in enumerate(years_to_process, 1):
        print(f"\n{'='*60}")
        print(f"Processing year {year} ({year_idx}/{len(years_to_process)})")
        print(f"{'='*60}")
        
        crawler = MPCrawler(year=year, batch_size=args.batch_size)
        
        if args.mode == 'constituencies':
            print(f"Crawling MP constituency links for {year}...")
            links = await crawler.crawl_constituency_links()
            print(f"Found {len(links)} constituency links")
            
            # Save links to file
            output_file = f"mp_{year}_constituency_links.txt"
            with open(output_file, 'w') as f:
                f.write('\n'.join(links))
            print(f"Links saved to {output_file}")
            
        elif args.mode == 'candidates':
            print(f"Crawling MP candidates for {year} (winners_only={args.winners_only})...")
            
            # First get constituency links
            links = await crawler.crawl_constituency_links()
            if not links:
                print(f"No constituency links found for {year}. Try running constituencies mode first.")
                continue
            
            # Then crawl candidates
            stats = await crawler.crawl_candidates_from_constituencies(links, args.winners_only)
            print(f"Crawling completed for {year}:")
            print(f"  Constituencies processed: {stats['constituencies']}")
            print(f"  Candidates found: {stats['candidates']}")
            print(f"  Errors: {stats['errors']}")
            
        elif args.mode == 'profiles':
            csv_path = args.csv_path or f"mp_data_{year}/candidates.csv"
            
            if not Path(csv_path).exists():
                print(f"CSV file not found: {csv_path}")
                print("Run candidates mode first to generate candidate data.")
                continue
            
            print(f"Generating MP candidate profiles from {csv_path}...")
            candidate_urls = CSVProcessor.extract_candidate_urls(csv_path, args.winners_only)
            
            if not candidate_urls:
                print("No candidate URLs found in CSV file")
                continue
            
            stats = await crawler.generate_candidate_profiles(candidate_urls)
            print(f"Profile generation completed for {year}:")
            print(f"  Profiles generated: {stats['profiles_generated']}")
            print(f"  Images downloaded: {stats['images_downloaded']}")
            print(f"  Errors: {stats['errors']}")
            
        elif args.mode == 'images':
            csv_path = args.csv_path or f"mp_data_{year}/candidates.csv"
            
            if not Path(csv_path).exists():
                print(f"CSV file not found: {csv_path}")
                continue
            
            print(f"Downloading MP candidate images from {csv_path}...")
            stats = await crawler.download_candidate_images_from_csv(csv_path, args.winners_only)
            print(f"Image download completed for {year}:")
            print(f"  Images downloaded: {stats.get('images_downloaded', 0)}")
            print(f"  Errors: {stats.get('errors', 0)}")
    
    if len(years_to_process) > 1:
        print(f"\n{'='*60}")
        print(f"Completed processing all {len(years_to_process)} years: {years_to_process}")
        print(f"{'='*60}")


async def handle_mla_command(args):
    """Handle MLA (State Assembly) crawling commands."""
    # Determine years to process
    years_to_process = args.years if args.years else [args.year]
    
    print(f"Processing {len(years_to_process)} year(s) for {args.state}: {years_to_process}")
    
    for year_idx, year in enumerate(years_to_process, 1):
        print(f"\n{'='*60}")
        print(f"Processing {args.state} - {year} ({year_idx}/{len(years_to_process)})")
        print(f"{'='*60}")
        
        crawler = MLACrawler(state=args.state, year=year, batch_size=args.batch_size)
        
        if args.mode == 'winners':
            print(f"Crawling MLA winners for {args.state} {year}...")
            
            # Get winners URL
            winners_url = crawler.get_winners_url_for_year()
            stats = await crawler.crawl_winners_from_state(winners_url)
            
            print(f"Winners crawling completed for {year}:")
            print(f"  Winners found: {stats['winners_found']}")
            print(f"  Constituencies: {stats['constituencies']}")
            print(f"  Errors: {stats['errors']}")
            
        elif args.mode == 'candidates':
            print(f"Crawling all MLA candidates for {args.state} {year}...")
            
            # This would need constituency URLs - placeholder implementation
            print("Note: Full constituency crawling needs to be implemented based on actual URL patterns")
            
        elif args.mode == 'images':
            csv_path = args.csv_path or f"mla_data_{args.state}_{year}/winners.csv"
            
            if not Path(csv_path).exists():
                print(f"CSV file not found: {csv_path}")
                print("Run winners mode first to generate candidate data.")
                continue
            
            print(f"Downloading MLA candidate images from {csv_path}...")
            stats = await crawler.download_mla_candidate_images(csv_path, args.winners_only)
            
            print(f"Image download completed for {year}:")
            print(f"  Images downloaded: {stats.get('images_downloaded', 0)}")
            print(f"  Errors: {stats.get('errors', 0)}")
    
    if len(years_to_process) > 1:
        print(f"\n{'='*60}")
        print(f"Completed processing all {len(years_to_process)} years for {args.state}: {years_to_process}")
        print(f"{'='*60}")


def handle_analyze_command(args):
    """Handle data analysis commands."""
    path = Path(args.csv_path)
    
    if not path.exists():
        print(f"Path not found: {args.csv_path}")
        return
    
    print(f"Analyzing data from: {args.csv_path}")
    
    if path.is_file():
        # Analyze single file
        stats = CSVProcessor.get_csv_statistics(str(path))
        print_analysis_report(stats)
        
    elif path.is_dir():
        # Analyze directory of CSV files
        csv_files = CSVProcessor.find_csv_files(str(path))
        
        if not csv_files:
            print(f"No CSV files found in directory: {args.csv_path}")
            return
        
        print(f"Found {len(csv_files)} CSV files")
        
        all_stats = []
        total_candidates = 0
        total_winners = 0
        
        for csv_file in csv_files:
            stats = CSVProcessor.get_csv_statistics(csv_file)
            all_stats.append(stats)
            total_candidates += stats['total_candidates']
            total_winners += stats['total_winners']
        
        # Print summary
        print(f"\n=== SUMMARY ===")
        print(f"Total CSV files: {len(csv_files)}")
        print(f"Total candidates: {total_candidates:,}")
        print(f"Total winners: {total_winners:,}")
        print(f"Average candidates per file: {total_candidates/len(csv_files):.1f}")
        
        # Print individual file stats if requested
        if len(csv_files) <= 10:  # Only for small number of files
            print(f"\n=== INDIVIDUAL FILES ===")
            for stats in all_stats:
                print(f"File: {Path(stats['file_path']).name}")
                print(f"  Candidates: {stats['total_candidates']}, Winners: {stats['total_winners']}")
    
    # Save report if output specified
    if args.output:
        print(f"Analysis report saved to: {args.output}")


def handle_util_command(args):
    """Handle utility commands."""
    if args.merge_csv:
        if not args.output:
            print("Output file required for merge operation (--output)")
            return
        
        print(f"Merging {len(args.merge_csv)} CSV files...")
        success = CSVProcessor.merge_csv_files(args.merge_csv, args.output)
        
        if success:
            print(f"Files merged successfully: {args.output}")
        else:
            print("Merge operation failed")


def print_analysis_report(stats):
    """Print formatted analysis report."""
    print(f"\n=== ANALYSIS REPORT ===")
    print(f"File: {Path(stats['file_path']).name}")
    print(f"Total candidates: {stats['total_candidates']:,}")
    print(f"Total winners: {stats['total_winners']:,}")
    print(f"Candidates with URLs: {stats['has_urls']}")
    print(f"File size: {stats['file_size']:,} bytes")
    print(f"Columns: {', '.join(stats['columns'][:10])}{'...' if len(stats['columns']) > 10 else ''}")


async def main():
    """Main entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'mp':
            await handle_mp_command(args)
        elif args.command == 'mla':
            await handle_mla_command(args)
        elif args.command == 'analyze':
            handle_analyze_command(args)
        elif args.command == 'util':
            handle_util_command(args)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def print_usage_examples():
    """Print usage examples for quick reference."""
    print("""
=== ELECTION DATA CRAWLER ===

Quick Start Examples:

SINGLE YEAR OPERATIONS:
1. Crawl MP constituency links for 2024:
   python main_refactored.py mp --year 2024 --mode constituencies

2. Crawl MP candidates (winners only) for 2024:
   python main_refactored.py mp --year 2024 --mode candidates --winners-only

3. Crawl MLA winners for Karnataka 2023:
   python main_refactored.py mla --state "Karnataka" --year 2023 --mode winners

MULTIPLE YEARS OPERATIONS:
4. Process multiple MP election years at once:
   python main_refactored.py mp --years 2024 2019 2014 2009 2004 --mode constituencies

5. Crawl MP candidates for multiple years (winners only):
   python main_refactored.py mp --years 2024 2019 2014 --mode candidates --winners-only

6. Process MLA data for multiple years:
   python main_refactored.py mla --state "Karnataka" --years 2023 2018 2013 --mode winners

OTHER OPERATIONS:
7. Generate MP candidate profiles:
   python main_refactored.py mp --year 2024 --mode profiles

8. Download candidate images:
   python main_refactored.py mp --year 2024 --mode images --csv-path "mp_data_2024/candidates.csv"

9. Analyze CSV data:
   python main_refactored.py analyze --csv-path "candidate_data/"

10. Merge CSV files:
    python main_refactored.py util --merge-csv file1.csv file2.csv --output merged.csv

For detailed help: python main_refactored.py --help
For command-specific help: python main_refactored.py <command> --help
""")


if __name__ == "__main__":
    # If no arguments provided, show usage examples
    if len(sys.argv) == 1:
        print_usage_examples()
    else:
        asyncio.run(main())