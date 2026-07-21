"""
Jupyter Notebook to HTML Converter with Collapsed Cell Support

This script converts a Jupyter notebook (.ipynb) to HTML while respecting
collapsed/folded cells (those with source_hidden=true in their metadata).

Collapsed cells are displayed with only their first line visible followed
by bullet points (•••), and are styled in gray to indicate hidden content.

Usage:
    python convert_to_respect_collapsed_folded_code_and_allow_equations.py <notebook_file.ipynb>

Example:
    python convert_to_respect_collapsed_folded_code_and_allow_equations.py Plates_vs_Flasks_Cost_analysis.ipynb

Output:
    Creates an HTML file with the same base name as the input notebook.
    For example: Plates_vs_Flasks_Cost_analysis.ipynb -> Plates_vs_Flasks_Cost_analysis.html

Features:
    - Preserves MathJax equation rendering
    - Respects Jupyter's source_hidden metadata for collapsed cells
    - Applies gray styling to collapsed code for visual distinction
    - Hides the "In [n]:" prompt for collapsed cells while maintaining alignment
    - Keeps outputs visible for all cells
"""

from nbconvert import HTMLExporter
from nbconvert.preprocessors import Preprocessor
import nbformat
import sys
import os

class HideSourcePreprocessor(Preprocessor):
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code':
            # Check for source_hidden in the nested jupyter metadata
            jupyter_meta = cell.metadata.get('jupyter', {})
            if jupyter_meta.get('source_hidden', False):
                # Get the first line and add bullet ellipsis
                lines = cell.source.split('\n')
                if lines:
                    cell.source = lines[0] + ' •••'
                else:
                    cell.source = ' ••• '
        return cell, resources

# Get input filename from command line argument
input_file = sys.argv[1]

# Generate output filename by replacing extension with .html
output_file = os.path.splitext(input_file)[0] + '.html'

# Load notebook
with open(input_file, 'r') as f:
    nb = nbformat.read(f, as_version=4)

# Create exporter with custom preprocessor
html_exporter = HTMLExporter()
html_exporter.register_preprocessor(HideSourcePreprocessor, enabled=True)

# Convert
(body, resources) = html_exporter.from_notebook_node(nb)

# Add custom CSS and JavaScript to style collapsed cells
custom_css = """
<style>
/* Style for collapsed cells */
.collapsed-cell-marker {
    color: #888 !important;
}
</style>
<script>
// JavaScript to add gray styling and hide prompts for cells with •••
document.addEventListener('DOMContentLoaded', function() {
    const codeCells = document.querySelectorAll('.jp-CodeCell');
    codeCells.forEach(cell => {
        const inputArea = cell.querySelector('.jp-InputArea');
        if (inputArea && inputArea.textContent.includes('•••')) {
            // Style the code gray
            const highlight = inputArea.querySelector('.highlight');
            if (highlight) {
                highlight.style.color = '#888';
                highlight.querySelectorAll('*').forEach(el => {
                    el.style.color = '#888';
                });
            }
            
            // Make the "In [n]:" prompt invisible but keep the space
            const prompt = cell.querySelector('.jp-InputPrompt');
            if (prompt) {
                prompt.style.visibility = 'hidden';
            }
        }
    });
});
</script>
"""

# Insert CSS before closing </head> tag
body = body.replace('</head>', custom_css + '</head>')

# Save
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(body)

print(f"Saved to {output_file}")