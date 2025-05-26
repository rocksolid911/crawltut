# examples/complete_usage_examples.py
"""
Complete usage examples for the election data extraction system
"""
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import ElectionDataExtractor
from processors.csv_processor import CSVProcessor
from processors.profile_processor import ProfileProcessor
from utils.file_manager import ElectionFileManager
from config.election_config import ELECTION_CONFIGS


async def step_by_step_andhra_pradesh_example():
    """Step-by-step example: Extract Andhra Pradesh Assembly data"""
    print("🚀 STEP-BY-STEP ANDHRA PRADESH ASSEMBLY EXTRACTION")
    print("=" * 60)
    print()

    print("📁 Target folder structure:")
    print("state_assembly/ANDHRA PRADESH/{district}/{candidate_name}/{candidate_name}_mla.json")
    print()

    extractor = ElectionDataExtractor()

    # ========== STEP 1: Extract constituency links ==========
    print("📋 STEP 1: Extracting constituency links...")
    print("-" * 40)
    try:
        await extractor.extract_constituencies(
            "https://www.myneta.info/AndhraPradesh2024/",
            election_type="andhra_pradesh"
        )
        print("✅ SUCCESS: Constituency links extracted!")
        print("📂 Files created:")
        print("   - state_assembly/ANDHRA PRADESH/constituencies_links_2024.md")
        print("   - state_assembly/ANDHRA PRADESH/constituencies_links_2024.txt")
        print("   - state_assembly/ANDHRA PRADESH/raw_result_2024.html")
    except Exception as e:
        print(f"❌ ERROR in Step 1: {e}")
        return
    print()

    # ========== STEP 2: Extract candidate data ==========
    print("👥 STEP 2: Extracting candidate data from constituencies...")
    print("-" * 40)
    try:
        await extractor.extract_candidates("2024", "andhra_pradesh")
        print("✅ SUCCESS: Candidate data extracted!")
        print("📂 Data saved to: state_assembly/ANDHRA PRADESH/{district}/")
        print("   Example: state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM_123.md")
    except Exception as e:
        print(f"❌ ERROR in Step 2: {e}")
        return
    print()

    # ========== STEP 3: Convert markdown to CSV ==========
    print("📊 STEP 3: Converting candidate data to CSV format...")
    print("-" * 40)
    try:
        config = ELECTION_CONFIGS["andhra_pradesh"]
        csv_processor = CSVProcessor(config)
        csv_processor.extract_candidate_tables_to_csv()
        print("✅ SUCCESS: CSV files created!")
        print("📂 CSV files location:")
        print("   - state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv")
        print("   - state_assembly/ANDHRA PRADESH/VIJAYAWADA/VIJAYAWADA.csv")
        print("   - (and other districts...)")
    except Exception as e:
        print(f"❌ ERROR in Step 3: {e}")
        return
    print()

    # ========== STEP 4: Extract detailed profiles ==========
    print("🤖 STEP 4: Extracting detailed candidate profiles...")
    print("-" * 40)
    print("Now you can extract detailed profiles using:")
    print()
    print("🔧 COMMAND OPTIONS:")
    print("A) Extract ALL candidates:")
    print(
        "   python cli.py profiles --csv-path 'state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' --election-type andhra_pradesh")
    print()
    print("B) Extract WINNERS ONLY:")
    print(
        "   python cli.py profiles --csv-path 'state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' --election-type andhra_pradesh --winners-only")
    print()
    print("📁 Profile files will be created as:")
    print("   state_assembly/ANDHRA PRADESH/AMALAPURAM/Dorababu_Yalla/Dorababu_Yalla_mla.json")
    print("   state_assembly/ANDHRA PRADESH/AMALAPURAM/Pawan_Kalyan/Pawan_Kalyan_mla.json")
    print()

    print("🎉 COMPLETE! Your Andhra Pradesh Assembly data extraction is ready!")
    print("=" * 60)


async def verify_existing_lok_sabha_data():
    """Verify that existing Lok Sabha data structure is preserved"""
    print("🔍 VERIFYING LOK SABHA DATA COMPATIBILITY")
    print("=" * 50)
    print()

    print("📁 Your existing Lok Sabha structure (UNCHANGED):")
    print("constituency_data/2024/ANDHRA PRADESH/AMALAPURAM/Dorababu_Yalla/Dorababu_Yalla.json")
    print()

    # Check if existing data exists
    existing_paths = [
        "constituency_data/2024",
        "constituency_data/2024/ANDHRA PRADESH",
    ]

    print("🔍 Checking existing data...")
    for path in existing_paths:
        if os.path.exists(path):
            print(f"✅ Found: {path}")
        else:
            print(f"ℹ️  Not found: {path} (will be created when needed)")
    print()

    print("🧪 TESTING LOK SABHA COMMANDS:")
    print("1️⃣ Process existing CSV data:")
    print("   python cli.py csv --election-type lok_sabha")
    print()
    print("2️⃣ Extract new Lok Sabha data:")
    print("   python cli.py constituencies --url 'https://www.myneta.info/LokSabha2024/' --election-type lok_sabha")
    print("   python cli.py candidates --year 2024 --election-type lok_sabha --state KARNATAKA")
    print()
    print("3️⃣ Extract detailed profiles (creates .json files):")
    print(
        "   python cli.py profiles --csv-path 'constituency_data/2024/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' --election-type lok_sabha")
    print()

    print("✅ Your existing Lok Sabha data continues to work exactly as before!")
    print("=" * 50)


def demonstrate_cli_commands():
    """Demonstrate all CLI commands with practical examples"""
    print("💻 CLI COMMANDS DEMONSTRATION")
    print("=" * 40)
    print()

    print("🏛️ ANDHRA PRADESH ASSEMBLY COMMANDS:")
    print("-" * 30)
    print("Step 1 - Extract constituencies:")
    print("python cli.py constituencies \\")
    print("    --url 'https://www.myneta.info/AndhraPradesh2024/' \\")
    print("    --election-type andhra_pradesh")
    print()

    print("Step 2 - Extract candidates:")
    print("python cli.py candidates \\")
    print("    --year 2024 \\")
    print("    --election-type andhra_pradesh")
    print()

    print("Step 3 - Generate CSV files:")
    print("python cli.py csv \\")
    print("    --election-type andhra_pradesh")
    print()

    print("Step 4 - Extract detailed profiles:")
    print("# All candidates:")
    print("python cli.py profiles \\")
    print("    --csv-path 'state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' \\")
    print("    --election-type andhra_pradesh")
    print()
    print("# Winners only:")
    print("python cli.py profiles \\")
    print("    --csv-path 'state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' \\")
    print("    --election-type andhra_pradesh \\")
    print("    --winners-only")
    print()

    print("🏛️ LOK SABHA COMMANDS (Existing structure):")
    print("-" * 30)
    print("Extract constituencies:")
    print("python cli.py constituencies \\")
    print("    --url 'https://www.myneta.info/LokSabha2024/' \\")
    print("    --election-type lok_sabha")
    print()

    print("Extract candidates for specific state:")
    print("python cli.py candidates \\")
    print("    --year 2024 \\")
    print("    --election-type lok_sabha \\")
    print("    --state KARNATAKA")
    print()

    print("Extract detailed profiles:")
    print("python cli.py profiles \\")
    print("    --csv-path 'constituency_data/2024/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' \\")
    print("    --election-type lok_sabha")
    print()


async def python_api_examples():
    """Show how to use the Python API directly"""
    print("🐍 PYTHON API USAGE EXAMPLES")
    print("=" * 40)
    print()

    print("📋 Example 1: Basic API usage")
    print("-" * 20)
    print("""
from main import ElectionDataExtractor

async def extract_assembly_data():
    extractor = ElectionDataExtractor()

    # Extract Andhra Pradesh Assembly
    await extractor.extract_constituencies(
        "https://www.myneta.info/AndhraPradesh2024/",
        election_type="andhra_pradesh"
    )

    # Extract candidate data
    await extractor.extract_candidates("2024", "andhra_pradesh")

# Run it
asyncio.run(extract_assembly_data())
""")

    print("📊 Example 2: CSV processing")
    print("-" * 20)
    print("""
from processors.csv_processor import CSVProcessor
from config.election_config import ELECTION_CONFIGS

# Process markdown files to CSV
config = ELECTION_CONFIGS["andhra_pradesh"]
csv_processor = CSVProcessor(config)
csv_processor.extract_candidate_tables_to_csv()
""")

    print("🤖 Example 3: Profile extraction")
    print("-" * 20)
    print("""
from processors.profile_processor import ProfileProcessor
from utils.file_manager import ElectionFileManager

async def extract_profiles():
    config = ELECTION_CONFIGS["andhra_pradesh"]
    file_manager = ElectionFileManager()
    processor = ProfileProcessor(config, file_manager)

    # Extract profiles for winners only
    await processor.process_candidates_from_csv(
        "state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv",
        winners_only=True,
        batch_size=5
    )

asyncio.run(extract_profiles())
""")


def show_file_naming_examples():
    """Show concrete examples of file naming patterns"""
    print("🏷️ FILE NAMING PATTERNS")
    print("=" * 30)
    print()

    print("📁 LOK SABHA (MP) - Existing naming preserved:")
    print("constituency_data/2024/ANDHRA PRADESH/AMALAPURAM/")
    print("├── Dorababu_Yalla/")
    print("│   └── Dorababu_Yalla.json           ← MP file")
    print("├── Pawan_Kalyan/")
    print("│   └── Pawan_Kalyan.json             ← MP file")
    print("├── Y_S_Jagan_Mohan_Reddy/")
    print("│   └── Y_S_Jagan_Mohan_Reddy.json    ← MP file")
    print("└── AMALAPURAM.csv")
    print()

    print("📁 STATE ASSEMBLY (MLA) - New _mla naming:")
    print("state_assembly/ANDHRA PRADESH/AMALAPURAM/")
    print("├── Dorababu_Yalla/")
    print("│   └── Dorababu_Yalla_mla.json       ← MLA file")
    print("├── Pawan_Kalyan/")
    print("│   └── Pawan_Kalyan_mla.json         ← MLA file")
    print("├── Y_S_Jagan_Mohan_Reddy/")
    print("│   └── Y_S_Jagan_Mohan_Reddy_mla.json ← MLA file")
    print("└── AMALAPURAM.csv")
    print()

    print("✨ Benefits:")
    print("✅ Easy to distinguish MP vs MLA data")
    print("✅ Candidate name remains in filename")
    print("✅ Consistent with existing MP naming pattern")
    print("✅ Clear identification of election type")


def show_folder_comparison():
    """Show side-by-side folder structure comparison"""
    print("📊 FOLDER STRUCTURE COMPARISON")
    print("=" * 50)
    print()

    print("🔄 BEFORE (Your existing structure) vs AFTER (Enhanced system)")
    print()

    print("BEFORE - Only Lok Sabha:")
    print("constituency_data/")
    print("└── 2024/")
    print("    └── ANDHRA PRADESH/")
    print("        └── AMALAPURAM/")
    print("            ├── Dorababu_Yalla/")
    print("            │   └── Dorababu_Yalla.json")
    print("            └── AMALAPURAM.csv")
    print()

    print("AFTER - Both Lok Sabha + Assembly:")
    print("your-project/")
    print("├── constituency_data/          ← UNCHANGED")
    print("│   └── 2024/")
    print("│       └── ANDHRA PRADESH/")
    print("│           └── AMALAPURAM/")
    print("│               ├── Dorababu_Yalla/")
    print("│               │   └── Dorababu_Yalla.json      ← SAME")
    print("│               └── AMALAPURAM.csv")
    print("│")
    print("└── state_assembly/             ← NEW")
    print("    ├── ANDHRA PRADESH/")
    print("    │   └── AMALAPURAM/")
    print("    │       ├── Dorababu_Yalla/")
    print("    │       │   └── Dorababu_Yalla_mla.json      ← NEW")
    print("    │       └── AMALAPURAM.csv")
    print("    ├── KARNATAKA/")
    print("    └── TELANGANA/")
    print()

    print("🎯 KEY POINTS:")
    print("✅ Your existing data is 100% preserved")
    print("✅ New assembly data goes to separate folder")
    print("✅ Clear naming distinction: .json vs _mla.json")
    print("✅ Both structures work simultaneously")


async def complete_workflow_example():
    """Show a complete end-to-end workflow"""
    print("🔄 COMPLETE WORKFLOW EXAMPLE")
    print("=" * 40)
    print()

    print("🎯 Goal: Extract complete Andhra Pradesh Assembly election data")
    print()

    print("⏰ ESTIMATED TIME: 30-60 minutes (depending on network speed)")
    print()

    print("📋 WORKFLOW STEPS:")
    print()

    print("1️⃣ PREPARATION (1 minute)")
    print("   pip install -r requirements.txt")
    print("   # Ensure your AI module is integrated")
    print()

    print("2️⃣ EXTRACT CONSTITUENCY LINKS (2-3 minutes)")
    print("   python cli.py constituencies \\")
    print("       --url 'https://www.myneta.info/AndhraPradesh2024/' \\")
    print("       --election-type andhra_pradesh")
    print("   # Creates: state_assembly/ANDHRA PRADESH/constituencies_links_2024.md")
    print()

    print("3️⃣ EXTRACT CANDIDATE DATA (15-30 minutes)")
    print("   python cli.py candidates \\")
    print("       --year 2024 \\")
    print("       --election-type andhra_pradesh")
    print("   # Creates: markdown files for each constituency")
    print()

    print("4️⃣ GENERATE CSV FILES (1-2 minutes)")
    print("   python cli.py csv \\")
    print("       --election-type andhra_pradesh")
    print("   # Creates: CSV files in each district folder")
    print()

    print("5️⃣ EXTRACT DETAILED PROFILES (10-30 minutes)")
    print("   # For specific constituency:")
    print("   python cli.py profiles \\")
    print("       --csv-path 'state_assembly/ANDHRA PRADESH/AMALAPURAM/AMALAPURAM.csv' \\")
    print("       --election-type andhra_pradesh \\")
    print("       --winners-only")
    print()
    print("   # Or batch process all constituencies with a script")
    print()

    print("📊 FINAL RESULT:")
    print("✅ Complete candidate database with profiles")
    print("✅ CSV files for easy analysis")
    print("✅ JSON files for detailed information")
    print("✅ Markdown files for human-readable data")
    print()

    print("🎉 SUCCESS! You now have comprehensive Andhra Pradesh Assembly election data!")


def main_menu():
    """Interactive menu for running examples"""
    print("🚀 ELECTION DATA EXTRACTION SYSTEM - USAGE EXAMPLES")
    print("=" * 60)
    print()

    examples = {
        "1": ("Step-by-step Andhra Pradesh extraction", step_by_step_andhra_pradesh_example),
        "2": ("Verify existing Lok Sabha compatibility", verify_existing_lok_sabha_data),
        "3": ("CLI commands demonstration", demonstrate_cli_commands),
        "4": ("Python API examples", python_api_examples),
        "5": ("File naming patterns", show_file_naming_examples),
        "6": ("Folder structure comparison", show_folder_comparison),
        "7": ("Complete workflow example", complete_workflow_example),
    }

    print("📋 AVAILABLE EXAMPLES:")
    for key, (description, _) in examples.items():
        print(f"   {key}. {description}")
    print("   0. Show all examples")
    print()

    choice = input("🔢 Enter your choice (0-7): ").strip()
    print()

    if choice == "0":
        print("📖 SHOWING ALL EXAMPLES...")
        print("=" * 60)
        for key, (description, func) in examples.items():
            print(f"\n\n🔸 {description.upper()}")
            print("=" * len(description))
            if asyncio.iscoroutinefunction(func):
                asyncio.run(func())
            else:
                func()
    elif choice in examples:
        description, func = examples[choice]
        print(f"📖 {description.upper()}")
        print("=" * len(description))
        if asyncio.iscoroutinefunction(func):
            asyncio.run(func())
        else:
            func()
    else:
        print("❌ Invalid choice. Please run the script again and choose 0-7.")


if __name__ == "__main__":
    main_menu()