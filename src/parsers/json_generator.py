"""
JSON generation wrapper for candidate data.

This module wraps the existing AI CSV generation functionality.
"""
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional

from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

# Import the existing generate function
try:
    from old_working_code_mp.ai_csv_generation import generate
except ImportError:
    print("Warning: Could not import ai_csv_generation module")
    generate = None


@retry(
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception)
)
def generate_with_retry(markdown_content: str, output_file: str) -> None:
    """
    Generate JSON with retry logic using tenacity.

    Args:
        markdown_content: Markdown content to process
        output_file: Path to output JSON file
    """
    if generate is None:
        raise ImportError("AI CSV generation module not available")
    generate(markdown_content, output_file)


def generate_wrapper(markdown_content: str, output_file: str) -> None:
    """
    Wrapper function that handles the generate call safely with tenacity retry logic.

    Args:
        markdown_content: Markdown content to process
        output_file: Path to output JSON file
    """
    try:
        generate_with_retry(markdown_content, output_file)
        print(f"Successfully generated JSON for {output_file}")
    except Exception as e:
        print(f"Error in generate_wrapper after all retries: {e}")
        # Save error information to a file for debugging
        error_file = output_file.replace('.json', '_error.txt')
        with open(error_file, 'w') as f:
            f.write(f"Error after all retries: {str(e)}\n")
            f.write(f"Content length: {len(markdown_content)}\n")


async def generate_json_async(markdown_content: str, json_output_file: str,
                             force_regenerate: bool = False,
                             skip_if_force_regenerated: bool = True) -> None:
    """
    Generate JSON in a separate thread with force regenerate tracking.

    Args:
        markdown_content: Markdown content to process
        json_output_file: Path to output JSON file
        force_regenerate: If True, regenerate even if file exists
        skip_if_force_regenerated: If True, skip if already force-regenerated
    """
    # Check if we should skip generation
    if not force_regenerate and os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0:
        print(f"JSON file already exists, skipping generation for {os.path.basename(json_output_file)}")
        return

    # If force regenerating, check if already force-regenerated
    if force_regenerate and skip_if_force_regenerated and is_force_regenerated(json_output_file):
        timestamp = get_force_regenerated_timestamp(json_output_file)
        print(f"Already force-regenerated on {timestamp}, skipping {os.path.basename(json_output_file)}")
        return

    if force_regenerate and os.path.exists(json_output_file):
        if is_force_regenerated(json_output_file):
            print(f"Force regenerating JSON for {os.path.basename(json_output_file)} (overriding previous force generation)")
        else:
            print(f"Force regenerating JSON for {os.path.basename(json_output_file)}")

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as executor:
        await loop.run_in_executor(
            executor,
            generate_wrapper,
            markdown_content,
            json_output_file
        )

    # Mark as force-regenerated if this was a force regeneration
    if force_regenerate:
        mark_as_force_regenerated(json_output_file)


def mark_as_force_regenerated(json_output_file: str) -> None:
    """
    Create a flag file to mark this candidate as force-regenerated.

    Args:
        json_output_file: Path to JSON file
    """
    flag_file = json_output_file.replace('.json', '.force_regenerated')
    with open(flag_file, 'w') as f:
        f.write(datetime.now().isoformat())
    print(f"Marked as force-regenerated: {os.path.basename(flag_file)}")


def is_force_regenerated(json_output_file: str) -> bool:
    """
    Check if this candidate was already force-regenerated.

    Args:
        json_output_file: Path to JSON file

    Returns:
        True if already force-regenerated
    """
    flag_file = json_output_file.replace('.json', '.force_regenerated')
    return os.path.exists(flag_file)


def get_force_regenerated_timestamp(json_output_file: str) -> Optional[str]:
    """
    Get the timestamp when this candidate was force-regenerated.

    Args:
        json_output_file: Path to JSON file

    Returns:
        Timestamp string or None
    """
    flag_file = json_output_file.replace('.json', '.force_regenerated')
    if os.path.exists(flag_file):
        try:
            with open(flag_file, 'r') as f:
                return f.read().strip()
        except:
            return "Unknown"
    return None
