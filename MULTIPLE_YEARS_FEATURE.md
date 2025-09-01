# Multiple Years Support - New Feature

## 🎉 Enhancement Added

The CLI now supports processing **multiple years** in a single command, making it much more efficient for bulk data processing.

## 🔧 How to Use

### For MP (Lok Sabha) Elections

**Single Year (as before):**
```bash
python main_refactored.py mp --year 2024 --mode constituencies
```

**Multiple Years (NEW):**
```bash
# Process multiple years at once
python main_refactored.py mp --years 2024 2019 2014 2009 2004 --mode constituencies

# Crawl candidates for multiple years
python main_refactored.py mp --years 2024 2019 2014 --mode candidates --winners-only

# Generate profiles for multiple years
python main_refactored.py mp --years 2024 2019 --mode profiles
```

### For MLA (State Assembly) Elections

**Single Year (as before):**
```bash
python main_refactored.py mla --state "Karnataka" --year 2023 --mode winners
```

**Multiple Years (NEW):**
```bash
# Process multiple years for a state
python main_refactored.py mla --state "Karnataka" --years 2023 2018 2013 --mode winners

# Download images for multiple years
python main_refactored.py mla --state "Maharashtra" --years 2024 2019 2014 --mode images
```

## 📊 Output Format

When processing multiple years, you'll see organized output like this:

```
Processing 3 year(s): [2024, 2019, 2014]

============================================================
Processing year 2024 (1/3)
============================================================
Crawling MP constituency links for 2024...
Found 543 constituency links
Links saved to mp_2024_constituency_links.txt

============================================================
Processing year 2019 (2/3)
============================================================
Crawling MP constituency links for 2019...
Found 543 constituency links
Links saved to mp_2019_constituency_links.txt

============================================================
Processing year 2014 (3/3)
============================================================
Crawling MP constituency links for 2014...
Found 543 constituency links
Links saved to mp_2014_constituency_links.txt

============================================================
Completed processing all 3 years: [2024, 2019, 2014]
============================================================
```

## ⚙️ Technical Details

### Argument Structure
- **`--year`**: Single year (mutually exclusive with `--years`)
- **`--years`**: Multiple years (space-separated list)
- These arguments are **mutually exclusive** - you can use one or the other, not both

### Processing Logic
1. **Sequential Processing**: Years are processed one by one to avoid overwhelming the server
2. **Error Isolation**: If one year fails, the others continue processing
3. **Individual Output Files**: Each year gets its own output files (e.g., `mp_2024_data.csv`, `mp_2019_data.csv`)
4. **Progress Tracking**: Clear visual indicators of progress through multiple years

### Supported Commands
Both `--year` and `--years` work with all modes:
- ✅ `constituencies` 
- ✅ `candidates`
- ✅ `profiles`
- ✅ `images`
- ✅ `winners` (for MLA)

## 🚀 Benefits

### Efficiency
```bash
# OLD WAY: Multiple separate commands
python main_refactored.py mp --year 2024 --mode constituencies
python main_refactored.py mp --year 2019 --mode constituencies  
python main_refactored.py mp --year 2014 --mode constituencies
python main_refactored.py mp --year 2009 --mode constituencies

# NEW WAY: Single command
python main_refactored.py mp --years 2024 2019 2014 2009 --mode constituencies
```

### Use Cases
- **Historical Analysis**: Process all available election years at once
- **Comparative Studies**: Gather data across multiple election cycles
- **Bulk Operations**: Set up overnight processing for large datasets
- **Research Projects**: Efficiently collect comprehensive datasets

## 💡 Examples by Use Case

### Research: Get All Available MP Data
```bash
# Get constituency links for all major election years
python main_refactored.py mp --years 2024 2019 2014 2009 2004 --mode constituencies

# Then get candidate data (winners only for older years)
python main_refactored.py mp --years 2019 2014 2009 2004 --mode candidates --winners-only
```

### Analysis: Compare State Elections
```bash
# Get MLA winners for multiple Karnataka elections
python main_refactored.py mla --state "Karnataka" --years 2023 2018 2013 2008 --mode winners

# Get images for recent elections
python main_refactored.py mla --state "Karnataka" --years 2023 2018 --mode images
```

### Bulk Processing: Set Up Overnight Jobs
```bash
# Process all MP elections (this could run overnight)
python main_refactored.py mp --years 2024 2019 2014 2009 2004 1999 --mode candidates --batch-size 20

# Process multiple states and years for MLA
python main_refactored.py mla --state "Maharashtra" --years 2024 2019 2014 --mode winners
```

## 🔍 Help and Validation

### Check Available Options
```bash
# See all available options
python main_refactored.py mp --help
python main_refactored.py mla --help

# See examples
python main_refactored.py
```

### Error Handling
- **Invalid year combinations**: Clear error messages
- **Missing data**: Continues with other years if one fails
- **Keyboard interrupt**: Graceful cancellation
- **Year-specific failures**: Isolated to that year only

This enhancement makes the crawler much more powerful for researchers, analysts, and anyone needing to process historical election data efficiently!