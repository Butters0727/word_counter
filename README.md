# Word Counter for LaTeX

This tool counts the words in a LaTeX document, ignoring most commands, environments, comments, and mathematical expressions. It provides a total word count and a hierarchical breakdown by section and subsection.

## Usage

There are two ways to use the word counter:

### 1. From a File

Provide the path to your `.tex` file as a command-line argument.

```bash
python word_counter.py path/to/your/file.tex
```

### 2. From Pasted Text (stdin)

Run the script without any arguments. You can then paste your LaTeX code directly into the terminal. Press `Ctrl-D` on macOS/Linux or `Ctrl-Z` then `Enter` on Windows to signal the end of the input.

```bash
python word_counter.py
```

You can also pipe a file into the script:

```bash
cat path/to/your/file.tex | python word_counter.py
```

## Example Output

The script will produce a tree-like summary of the word counts:

```
Total Word Count: 850

- Preamble/Abstract: 150 words
- Section 1: Introduction (400 words)
  - Subsection 1.1: Background (250 words)
  - Subsection 1.2: Related Work (150 words)
- Section 2: Conclusion (300 words)
```

## How it Works

The script first parses the document to identify the structure based on `\section` and `\subsection}` commands. Then, for each section and subsection, it removes the following LaTeX elements before counting the words:
- Comments
- Common environments like `figure`, `table`, `equation`, etc.
- Math modes (`$...$`, `$$...$$`, `\[...\]`)
- Most standard LaTeX commands (e.g., `\cite{...}`, `\textbf{...}`)

The remaining text is then counted to provide a detailed breakdown and a total count.