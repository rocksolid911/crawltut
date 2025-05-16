import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, DefaultMarkdownGenerator, \
    PruningContentFilter


async def customcrawler():
    session_id = "session_id"
    browser_config = BrowserConfig(
        headless=False,
        browser_type="chromium",
         # Increase timeout to handle all the dropdowns
    )
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=10)
    )

    # Updated JavaScript to better handle dropdowns and ensure all items are captured
    js_command = """
    (function() {
        // Wait function to give time for dropdowns to appear
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        // Find all state links
        var stateLinks = document.querySelectorAll('.tab-content a');
        var allResults = {};

        // For each state, click and gather all constituencies
        for (var i = 0; i < stateLinks.length; i++) {
            var stateLink = stateLinks[i];
            var stateName = stateLink.textContent.trim();

            // Skip "ALL CONSTITUENCIES" links
            if (stateName === "ALL CONSTITUENCIES") {
                continue;
            }

            // Get the parent dropdown to find state name if not on the link
            if (stateName === "") {
                var parentHeader = stateLink.closest('.tab-pane').querySelector('h4');
                if (parentHeader) {
                    stateName = parentHeader.textContent.trim();
                } else {
                    stateName = "Unknown State " + i;
                }
            }

            // Capture the href attribute
            var href = stateLink.getAttribute('href');

            // Add to results
            if (!allResults[stateName]) {
                allResults[stateName] = [];
            }

            allResults[stateName].push({
                name: stateName,
                href: href
            });
        }

        // If the above doesn't work, try with specific dropdown selectors
        if (Object.keys(allResults).length === 0) {
            // Find all dropdown buttons
            var dropdownButtons = document.querySelectorAll('button[onclick*="handle_dropdown"]');

            // Process each dropdown button
            for (var i = 0; i < dropdownButtons.length; i++) {
                var button = dropdownButtons[i];
                var stateName = button.textContent.replace(/\\s*\\n.*$/, '').trim();

                // Extract dropdown ID from onclick attribute
                var onclickAttr = button.getAttribute('onclick');
                var match = onclickAttr.match(/handle_dropdown\\('item', '(\\d+)'\\)/);

                if (match) {
                    var dropdownId = match[1];

                    // Click to open the dropdown
                    button.click();

                    // Get the dropdown content element
                    var dropdownContent = document.getElementById('item_' + dropdownId);

                    // If dropdown is visible, get all links
                    if (dropdownContent) {
                        var links = dropdownContent.querySelectorAll('a');
                        allResults[stateName] = [];

                        // Skip the first link which is usually "ALL CONSTITUENCIES"
                        for (var j = 1; j < links.length; j++) {
                            var link = links[j];
                            allResults[stateName].push({
                                name: link.textContent.trim(),
                                href: link.getAttribute('href')
                            });
                        }
                    }

                    // Click again to close dropdown (optional)
                    button.click();
                }
            }
        }

        // Try a third method if needed - for the specific structure in the image
        if (Object.keys(allResults).length === 0) {
            var stateHeadings = document.querySelectorAll('td strong');

            for (var i = 0; i < stateHeadings.length; i++) {
                var heading = stateHeadings[i];
                var stateName = heading.textContent.trim();

                // Find the associated dropdown
                var dropdown = heading.closest('tr').nextElementSibling;
                if (dropdown) {
                    var links = dropdown.querySelectorAll('a');
                    allResults[stateName] = [];

                    for (var j = 0; j < links.length; j++) {
                        var link = links[j];
                        allResults[stateName].push({
                            name: link.textContent.trim(),
                            href: link.getAttribute('href')
                        });
                    }
                }
            }
        }

        // For the structure in the image, where all states are buttons with dropdowns
        if (Object.keys(allResults).length === 0) {
            var stateButtons = document.querySelectorAll('button.accordion');

            for (var i = 0; i < stateButtons.length; i++) {
                var button = stateButtons[i];
                var stateName = button.textContent.trim();

                // Click to open
                button.click();

                // Find all links in the panel that opens
                var panel = button.nextElementSibling;
                if (panel && panel.classList.contains('panel')) {
                    var links = panel.querySelectorAll('a');
                    allResults[stateName] = [];

                    for (var j = 0; j < links.length; j++) {
                        var link = links[j];
                        allResults[stateName].push({
                            name: link.textContent.trim(),
                            href: link.getAttribute('href')
                        });
                    }
                }

                // Close the panel
                button.click();
            }
        }

        // Method for the exact HTML structure in the image
        if (Object.keys(allResults).length === 0) {
            // Get all state elements
            var stateElements = document.querySelectorAll('.w3-third');

            for (var i = 0; i < stateElements.length; i++) {
                var stateElement = stateElements[i];
                var button = stateElement.querySelector('.dropbtnJS');

                if (button) {
                    var stateName = button.textContent.replace(/\\s*\\n.*$/, '').trim();

                    // Get the dropdown ID
                    var onclickAttr = button.getAttribute('onclick');
                    var match = onclickAttr.match(/handle_dropdown\\('item', '(\\d+)'\\)/);

                    if (match) {
                        // Click to open dropdown
                        var dropdownId = match[1];

                        // Get the original display style
                        var dropdownContent = document.getElementById('item_' + dropdownId);
                        var originalDisplay = dropdownContent ? dropdownContent.style.display : 'none';

                        // Force display to block to make sure we can see all items
                        if (dropdownContent) {
                            dropdownContent.style.display = 'block';

                            // Get all links
                            var links = dropdownContent.querySelectorAll('a');
                            allResults[stateName] = [];

                            // Skip first "ALL CONSTITUENCIES" link
                            for (var j = 1; j < links.length; j++) {
                                var link = links[j];
                                allResults[stateName].push({
                                    name: link.textContent.trim(),
                                    href: link.getAttribute('href')
                                });
                            }

                            // Restore original display style
                            dropdownContent.style.display = originalDisplay;
                        }
                    }
                }
            }
        }

        // Display results on page for visual confirmation
        var resultsContainer = document.createElement('div');
        resultsContainer.id = 'extracted-results';
        resultsContainer.style.padding = '20px';
        resultsContainer.style.background = '#f5f5f5';
        resultsContainer.style.margin = '20px';
        resultsContainer.style.border = '1px solid #ddd';

        var totalConstituencies = 0;
        var totalStates = Object.keys(allResults).length;

        var resultsHTML = '<h2>Extracted Constituencies with Links by State (' + totalStates + ' states)</h2>';
        for (var state in allResults) {
            if (allResults.hasOwnProperty(state)) {
                var constituencies = allResults[state];
                totalConstituencies += constituencies.length;
                resultsHTML += '<h3>' + state + ' (' + constituencies.length + ' constituencies)</h3><ul>';

                for (var j = 0; j < constituencies.length; j++) {
                    resultsHTML += '<li><a href="' + constituencies[j].href + '">' + 
                                   constituencies[j].name + '</a></li>';
                }
                resultsHTML += '</ul>';
            }
        }

        resultsHTML += '<p>Total: ' + totalConstituencies + ' constituencies across ' + totalStates + ' states</p>';

        resultsContainer.innerHTML = resultsHTML;
        document.body.appendChild(resultsContainer);
        window.scrollTo(0, document.body.scrollHeight);

        // Return the results as JSON string
        return JSON.stringify(allResults);
    })();
    """

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=js_command,
        markdown_generator=md_generator,
        session_id=session_id,

    )

    # async with AsyncWebCrawler(config=browser_config) as crawler:
    #     result = await crawler.arun(
    #         "https://www.myneta.info/LokSabha2024/",
    #         config=run_config
    #     )
    #
    #     # Save raw HTML to debug
    #     with open("raw_result.html", "w", encoding="utf-8") as f:
    #         f.write(result.cleaned_html)
    #
    # async  with AsyncWebCrawler(config=browser_config) as crawler:
    #     result = await crawler.arun(
    #         "raw:raw_result.html",
    #          config=run_config
    #     )

        # # Extract the JSON results
        # json_match = re.search(r'(\{.*})', result.cleaned_html)
        #
        # if json_match:
        #     try:
        #         # Parse the JSON data
        #         constituency_data = json.loads(json_match.group(1))
        #
        #         # Write to a text file
        #         with open("constituencies_links.txt", "w", encoding="utf-8") as f:
        #             f.write("CONSTITUENCY LINKS BY STATE\n")
        #             f.write("==========================\n\n")
        #
        #             total_constituencies = 0
        #
        #             for state, constituencies in constituency_data.items():
        #                 f.write(f"{state} ({len(constituencies)} constituencies)\n")
        #                 f.write("-" * (len(state) + 4 + len(str(len(constituencies))) + 16) + "\n")
        #
        #                 total_constituencies += len(constituencies)
        #
        #                 for constituency in constituencies:
        #                     # Create full URL if it's a relative path
        #                     href = constituency['href']
        #                     if href and href.startswith('index.php'):
        #                         href = f"https://www.myneta.info/LokSabha2024/{href}"
        #
        #                     f.write(f"  {constituency['name']}: {href}\n")
        #
        #                 f.write("\n")
        #
        #             f.write(
        #                 f"\nTotal: {total_constituencies} constituencies across {len(constituency_data)} states/UTs\n")
        #
        #         print(f"Successfully saved constituency links to constituencies_links.txt")
        #         print(f"Found {total_constituencies} constituencies across {len(constituency_data)} states/UTs")
        #
        #     except json.JSONDecodeError as e:
        #         print(f"Could not parse JSON results: {e}")
        #         # Try to extract JSON with a more lenient approach
        #         try:
        #             # Look for JSON-like content - anything between curly braces
        #             full_text = result.cleaned_html
        #             start_idx = full_text.find('{')
        #             end_idx = full_text.rfind('}') + 1
        #
        #             if 0 <= start_idx < end_idx:
        #                 json_str = full_text[start_idx:end_idx]
        #                 constituency_data = json.loads(json_str)
        #                 print("Found JSON data using alternative extraction method")
        #                 # Process the data as before...
        #             else:
        #                 print("No JSON-like content found in the result")
        #         except Exception as e2:
        #             print(f"Alternative JSON extraction also failed: {e2}")
        # else:
        #     print("No JSON results found in the response")

        # print("Crawled length:", len(result.cleaned_html))


