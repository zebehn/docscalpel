# DocScalpel - Quick Start Guide

**5-Minute Guide to Get Started**

---

## Installation

```bash
cd /path/to/docscalpel
pip install -r requirements.txt
```

---

## Basic Usage

### Extract Everything (Figures, Tables, Equations)

```bash
python -m docscalpel paper.pdf
```

### Extract Only Figures

```bash
python -m docscalpel paper.pdf --types figure
```

### Extract to Specific Folder

```bash
python -m docscalpel paper.pdf --output ./my_figures
```

---

## Common Commands

| What I Want | Command |
|-------------|---------|
| Extract figures only | `python -m docscalpel paper.pdf --types figure` |
| Extract tables only | `python -m docscalpel paper.pdf --types table` |
| Extract to folder | `python -m docscalpel paper.pdf --output ./extracted` |
| Get JSON output | `python -m docscalpel paper.pdf --format json` |
| High confidence only | `python -m docscalpel paper.pdf --confidence 0.8` |
| Add padding around elements | `python -m docscalpel paper.pdf --padding 10` |
| Process first 10 pages only | `python -m docscalpel paper.pdf --max-pages 10` |
| See detailed logs | `python -m docscalpel paper.pdf --verbose` |
| Get help | `python -m docscalpel --help` |

---

## Output

### Text Output (Default)

```
✅ Extraction completed successfully

📊 Extraction Statistics:
  Total elements: 5
  Figures: 3
  Tables: 2
  Time: 2.45s

📂 Output:
  Directory: ./extracted
```

**Files created**: `figure_01.pdf`, `figure_02.pdf`, `table_01.pdf`, etc.

### JSON Output

```bash
python -m docscalpel paper.pdf --format json
```

```json
{
  "success": true,
  "statistics": {
    "total_elements": 5,
    "figure_count": 3,
    "table_count": 2
  },
  "elements": [...]
}
```

---

## Real-World Examples

### Example 1: Extract Figures from Research Paper

```bash
python -m docscalpel research_paper.pdf \
  --types figure \
  --output ./figures \
  --confidence 0.7
```

### Example 2: Extract All Elements with Custom Names

```bash
python -m docscalpel paper.pdf \
  --types figure,table,equation \
  --output ./extracted \
  --naming-pattern "element_{counter:03d}.pdf"
```

### Example 3: Quick Test on First 20 Pages

```bash
python -m docscalpel large_paper.pdf \
  --max-pages 20 \
  --output ./test
```

### Example 4: JSON Output for Automation

```bash
python -m docscalpel paper.pdf --format json > results.json
cat results.json | jq '.statistics'
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "PDF file not found" | Check the file path: `ls paper.pdf` |
| "Invalid element type" | Use `figure`, `table`, or `equation` (singular) |
| "Confidence must be 0.0-1.0" | Use a value like `0.5` or `0.8`, not `1.5` |
| No elements detected | Try `--confidence 0.3` or `--verbose` to debug |
| Import errors | Run `pip install -r requirements.txt` |

---

## Next Steps

📖 **[Read the full manual](CLI_MANUAL.md)** for:
- Complete command reference
- Advanced features
- Batch processing examples
- Performance optimization
- JSON schema details

---

**Need Help?** Run `python -m docscalpel --help`
