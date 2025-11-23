"""
Generate realistic test PDF fixtures for testing the extraction library.

This script creates sample PDFs with various layouts and element types
to ensure comprehensive test coverage.
"""

import fitz  # PyMuPDF
from pathlib import Path

# Define colors
BLUE = (0, 0, 1)
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLACK = (0, 0, 0)


def create_pdf_with_three_figures():
    """
    Create a PDF with 3 figures for User Story 1 testing.

    Matches the spec requirement: PDF with 3 figures → 3 files created.
    """
    doc = fitz.open()

    # Page 1: Two figures
    page1 = doc.new_page(width=612, height=792)

    # Title
    page1.insert_text((72, 72), "Sample Research Paper", fontsize=18)
    page1.insert_text((72, 100), "Testing Figure Extraction", fontsize=14)

    # Figure 1: Chart/Graph region
    fig1_rect = fitz.Rect(100, 150, 400, 300)
    page1.draw_rect(fig1_rect, color=BLUE, width=2)
    page1.insert_text((150, 180), "Figure 1: Example Chart", fontsize=10)
    page1.draw_line((120, 220), (380, 220), color=BLACK)
    page1.draw_line((120, 250), (320, 200), color=RED)
    page1.insert_text((200, 310), "Caption: Sample data visualization", fontsize=8)

    # Figure 2: Diagram region
    fig2_rect = fitz.Rect(100, 350, 400, 520)
    page1.draw_rect(fig2_rect, color=BLUE, width=2)
    page1.insert_text((180, 380), "Figure 2: System Diagram", fontsize=10)
    # Draw simple flowchart boxes
    page1.draw_rect(fitz.Rect(150, 410, 350, 460), color=BLACK, width=1)
    page1.insert_text((220, 440), "Input", fontsize=9)
    page1.draw_line((250, 460), (250, 480), color=BLACK, width=2)
    page1.insert_text((200, 530), "Caption: Processing pipeline", fontsize=8)

    # Page 2: One figure
    page2 = doc.new_page(width=612, height=792)
    page2.insert_text((72, 72), "Continued...", fontsize=14)

    # Figure 3: Plot region
    fig3_rect = fitz.Rect(100, 150, 400, 350)
    page2.draw_rect(fig3_rect, color=BLUE, width=2)
    page2.insert_text((170, 180), "Figure 3: Performance Plot", fontsize=10)
    # Draw axes
    page2.draw_line((120, 300), (380, 300), color=BLACK, width=2)  # X-axis
    page2.draw_line((120, 200), (120, 300), color=BLACK, width=2)  # Y-axis
    # Plot line
    page2.draw_line((120, 280), (200, 240), color=RED, width=2)
    page2.draw_line((200, 240), (300, 220), color=RED, width=2)
    page2.insert_text((180, 360), "Caption: Accuracy over time", fontsize=8)

    output_path = Path(__file__).parent / "sample_paper_with_figures.pdf"
    doc.save(str(output_path))
    doc.close()
    print(f"✓ Created: {output_path.name}")


def create_pdf_with_mixed_elements():
    """
    Create a PDF with figures, tables, and equations for User Story 2 testing.

    Matches the spec requirement: PDF with 2 figures, 3 tables, 1 equation.
    """
    doc = fitz.open()

    # Page 1: Figures and table
    page1 = doc.new_page(width=612, height=792)
    page1.insert_text((72, 72), "Technical Paper - Mixed Content", fontsize=16)

    # Figure 1
    fig1_rect = fitz.Rect(80, 120, 280, 240)
    page1.draw_rect(fig1_rect, color=BLUE, width=2)
    page1.insert_text((130, 150), "Figure 1: Architecture", fontsize=9)
    page1.draw_rect(fitz.Rect(100, 170, 260, 220), color=BLACK, width=1)

    # Table 1
    table1_y = 280
    page1.insert_text((100, table1_y), "Table 1: Experimental Results", fontsize=9)
    # Draw table grid
    for i in range(5):  # 5 rows
        y = table1_y + 20 + (i * 25)
        page1.draw_line((80, y), (400, y), color=BLACK)
    for i in range(4):  # 4 columns
        x = 80 + (i * 80)
        page1.draw_line((x, table1_y + 20), (x, table1_y + 120), color=BLACK)
    # Add some text in cells
    page1.insert_text((90, table1_y + 35), "Method", fontsize=8)
    page1.insert_text((170, table1_y + 35), "Accuracy", fontsize=8)
    page1.insert_text((250, table1_y + 35), "Speed", fontsize=8)

    # Page 2: More tables and figure
    page2 = doc.new_page(width=612, height=792)

    # Table 2
    table2_y = 100
    page2.insert_text((100, table2_y), "Table 2: Performance Metrics", fontsize=9)
    for i in range(4):
        y = table2_y + 20 + (i * 30)
        page2.draw_line((80, y), (450, y), color=BLACK)
    for i in range(5):
        x = 80 + (i * 92.5)
        page2.draw_line((x, table2_y + 20), (x, table2_y + 110), color=BLACK)

    # Figure 2
    fig2_rect = fitz.Rect(80, 240, 300, 360)
    page2.draw_rect(fig2_rect, color=BLUE, width=2)
    page2.insert_text((140, 270), "Figure 2: Results", fontsize=9)
    page2.draw_line((100, 330), (280, 330), color=BLACK, width=2)
    page2.draw_line((100, 310), (200, 280), color=GREEN, width=2)

    # Table 3
    table3_y = 400
    page2.insert_text((100, table3_y), "Table 3: Comparison", fontsize=9)
    for i in range(3):
        y = table3_y + 20 + (i * 30)
        page2.draw_line((80, y), (350, y), color=BLACK)
    for i in range(3):
        x = 80 + (i * 90)
        page2.draw_line((x, table3_y + 20), (x, table3_y + 80), color=BLACK)

    # Page 3: Equation
    page3 = doc.new_page(width=612, height=792)
    page3.insert_text((72, 72), "Mathematical Analysis", fontsize=14)

    # Equation region (simulated with text and symbols)
    eq_rect = fitz.Rect(150, 150, 450, 220)
    page3.draw_rect(eq_rect, color=GREEN, width=2)
    page3.insert_text((200, 185), "f(x) = ∫ e^(-x²/2) dx", fontsize=14)
    page3.insert_text((260, 230), "(Equation 1)", fontsize=9)

    output_path = Path(__file__).parent / "sample_paper_mixed.pdf"
    doc.save(str(output_path))
    doc.close()
    print(f"✓ Created: {output_path.name}")


def create_text_only_pdf():
    """
    Create a PDF with only text (no figures/tables/equations).

    Used to test the "no elements detected" case.
    """
    doc = fitz.open()

    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 72), "Text-Only Research Paper", fontsize=16)
    page.insert_text((72, 100), "Abstract", fontsize=12)

    # Add paragraphs of text
    text_lines = [
        "This is a sample research paper that contains only text content.",
        "There are no figures, tables, or equations in this document.",
        "",
        "The purpose of this document is to test the extraction system's",
        "behavior when no visual elements are present. The system should",
        "complete successfully but report zero elements extracted.",
        "",
        "This validates the 'no elements detected' success case from the",
        "specification, ensuring graceful handling of text-only documents.",
    ]

    y = 130
    for line in text_lines:
        if line:
            page.insert_text((72, y), line, fontsize=11)
        y += 20

    output_path = Path(__file__).parent / "text_only_paper.pdf"
    doc.save(str(output_path))
    doc.close()
    print(f"✓ Created: {output_path.name}")


def create_large_pdf_for_performance():
    """
    Create a 20-page PDF for performance testing.

    Target: Process in under 30 seconds.
    """
    doc = fitz.open()

    for page_num in range(1, 21):
        page = doc.new_page(width=612, height=792)

        # Page header
        page.insert_text((72, 50), f"Page {page_num} of 20", fontsize=10)
        page.insert_text((72, 72), f"Performance Test Document", fontsize=14)

        # Add 2 figures per page
        fig1_y = 120
        fig1_rect = fitz.Rect(80, fig1_y, 280, fig1_y + 120)
        page.draw_rect(fig1_rect, color=BLUE, width=2)
        page.insert_text((120, fig1_y + 30), f"Figure {page_num}A", fontsize=10)

        fig2_y = 280
        fig2_rect = fitz.Rect(80, fig2_y, 280, fig2_y + 120)
        page.draw_rect(fig2_rect, color=BLUE, width=2)
        page.insert_text((120, fig2_y + 30), f"Figure {page_num}B", fontsize=10)

        # Add 1 table per page
        table_y = 450
        page.insert_text((100, table_y), f"Table {page_num}: Data", fontsize=9)
        for i in range(4):
            y = table_y + 20 + (i * 25)
            page.draw_line((80, y), (350, y), color=BLACK)
        for i in range(3):
            x = 80 + (i * 90)
            page.draw_line((x, table_y + 20), (x, table_y + 95), color=BLACK)

    output_path = Path(__file__).parent / "large_paper_20pages.pdf"
    doc.save(str(output_path))
    doc.close()
    print(f"✓ Created: {output_path.name} (20 pages, ~40 figures, ~20 tables)")


def create_high_density_pdf():
    """
    Create a PDF with many elements on a single page.

    Tests extraction with high element density and potential overlaps.
    """
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)

    page.insert_text((72, 50), "High-Density Element Test", fontsize=14)

    # Create grid of small figures
    cols = 3
    rows = 4
    width = 150
    height = 100
    x_spacing = 170
    y_spacing = 120
    x_start = 50
    y_start = 100

    fig_num = 1
    for row in range(rows):
        for col in range(cols):
            x = x_start + (col * x_spacing)
            y = y_start + (row * y_spacing)

            rect = fitz.Rect(x, y, x + width, y + height)
            page.draw_rect(rect, color=BLUE, width=1)
            page.insert_text((x + 40, y + 50), f"Fig {fig_num}", fontsize=8)
            fig_num += 1

    output_path = Path(__file__).parent / "high_density_paper.pdf"
    doc.save(str(output_path))
    doc.close()
    print(f"✓ Created: {output_path.name} (12 figures on 1 page)")


def main():
    """Generate all test PDF fixtures."""
    print("Generating test PDF fixtures...\n")

    create_pdf_with_three_figures()
    create_pdf_with_mixed_elements()
    create_text_only_pdf()
    create_large_pdf_for_performance()
    create_high_density_pdf()

    print(f"\n✅ All test fixtures created successfully!")
    print(f"\nFixtures location: {Path(__file__).parent}")
    print("\nCreated files:")
    print("  - sample_paper_with_figures.pdf (3 figures)")
    print("  - sample_paper_mixed.pdf (2 figures, 3 tables, 1 equation)")
    print("  - text_only_paper.pdf (no elements)")
    print("  - large_paper_20pages.pdf (20 pages for performance testing)")
    print("  - high_density_paper.pdf (12 figures on 1 page)")


if __name__ == "__main__":
    main()
