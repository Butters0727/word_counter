import argparse
import re
import sys

def clean_latex(content):
    """
    Removes LaTeX commands, environments, and comments from a chunk of text.
    Returns plain text.
    """
    # Remove comments
    content = re.sub(r'%.*', '', content)

    # Remove common environments that don't contain countable text
    environments_to_remove = ['equation', 'figure', 'table', 'tabular', 'thebibliography', 'verbatim', 'tikzpicture']
    for env in environments_to_remove:
        content = re.sub(r'\\begin{' + env + r'}[\s\S]*?\\end{' + env + r'}', '', content, flags=re.MULTILINE)
        content = re.sub(r'\\begin{' + env + r'\*}[\s\S]*?\\end{' + env + r'\*}', '', content, flags=re.MULTILINE)

    # Remove math modes
    content = re.sub(r'\$\$[\s\S]*?\$\$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\\\[[\s\S]*?\\\]', '', content, flags=re.MULTILINE)
    content = re.sub(r'\$.*?\$', '', content)

    # Remove commands with arguments (non-greedy)
    content = re.sub(r'\\[a-zA-Z]+(?:\\[[^\]]*?\])?(?:\{.*?\})?', '', content)

    # Remove commands without arguments
    content = re.sub(r'\\[a-zA-Z]+', '', content)

    # Remove any remaining curly braces
    content = re.sub(r'[\{\}]', '', content)
    
    # Remove leading/trailing whitespace from each line
    content = "\n".join([line.strip() for line in content.splitlines()])

    return content

def count_words(text):
    """Counts the words in a given string."""
    return len(text.split())

def parse_and_count(content):
    """
    Parses the content, counts words, and prints the results.
    Detects if the content is likely plain text or LaTeX and adjusts output.
    """
    # Simple check to guess if the content is plain text or LaTeX
    is_latex = r'\section' in content or r'\subsection' in content or r'\documentclass' in content

    if not is_latex:
        # Plain text mode
        word_count = count_words(content)
        print(f"Total Word Count: {word_count}")
        return

    # LaTeX mode
    # Regex to find section and subsection titles
    section_pattern = r'\\section\*?{([^}]+)}'
    subsection_pattern = r'\\subsection\*?{([^}]+)}'

    # Split the document by sections
    sections = re.split(r'(' + section_pattern + ')', content)
    
    results = {'total_words': 0, 'preamble': {}, 'sections': []}

    # Handle text before the first section (preamble/abstract)
    preamble_content = sections[0]
    preamble_cleaned = clean_latex(preamble_content)
    preamble_word_count = count_words(preamble_cleaned)
    if preamble_word_count > 0:
        results['preamble'] = {'word_count': preamble_word_count}
        results['total_words'] += preamble_word_count

    # Process each section
    for i in range(1, len(sections), 2):
        section_title_match = re.search(section_pattern, sections[i])
        if not section_title_match:
            continue
        
        section_title = section_title_match.group(1)
        section_content = sections[i+1]
        
        section_data = {'title': section_title, 'word_count': 0, 'subsections': []}

        # Split the section content by subsections
        subsections = re.split(r'(' + subsection_pattern + ')', section_content)
        
        # Handle text within the section but before the first subsection
        section_intro_content = subsections[0]
        section_intro_cleaned = clean_latex(section_intro_content)
        section_intro_word_count = count_words(section_intro_cleaned)
        section_data['word_count'] += section_intro_word_count
        
        # Process each subsection
        for j in range(1, len(subsections), 2):
            subsection_title_match = re.search(subsection_pattern, subsections[j])
            if not subsection_title_match:
                continue

            subsection_title = subsection_title_match.group(1)
            subsection_content = subsections[j+1]
            
            subsection_cleaned = clean_latex(subsection_content)
            subsection_word_count = count_words(subsection_cleaned)
            
            if subsection_word_count > 0:
                subsection_data = {'title': subsection_title, 'word_count': subsection_word_count}
                section_data['subsections'].append(subsection_data)
                section_data['word_count'] += subsection_word_count

        results['sections'].append(section_data)
        results['total_words'] += section_data['word_count']

    print_results(results)

def print_results(results):
    """Prints the word count results in a tree format."""
    print(f"Total Word Count: {results['total_words']}\n")

    if results.get('preamble'):
        print(f"- Preamble/Abstract: {results['preamble']['word_count']} words")

    for i, section in enumerate(results['sections'], 1):
        print(f"- Section {i}: {section['title']} ({section['word_count']} words)")
        for j, subsection in enumerate(section['subsections'], 1):
            print(f"  - Subsection {i}.{j}: {subsection['title']} ({subsection['word_count']} words)")

def main():
    """Main function to handle input and start the process."""
    parser = argparse.ArgumentParser(
        description='Count words in a LaTeX file hierarchically.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  - Count words from a file:
    python word_counter.py my_paper.tex

  - Count words from pasted text (pipe from stdin):
    cat my_paper.tex | python word_counter.py
    (or just run the script and paste your text, then press Ctrl-D)
"""
    )
    parser.add_argument('file', nargs='?', type=str, help='The path to the .tex file. If not provided, reads from stdin.')
    args = parser.parse_args()

    content = ""
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        # Check if stdin is connected to a terminal or a pipe
        if sys.stdin.isatty():
             print("Please paste your LaTeX code below and press Ctrl-D when you're done.", file=sys.stderr)
        content = sys.stdin.read()

    if not content.strip():
        print("Error: No input received.", file=sys.stderr)
        sys.exit(1)

    parse_and_count(content)

if __name__ == '__main__':
    main()