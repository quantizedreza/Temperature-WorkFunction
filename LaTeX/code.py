from pathlib import Path
from PIL import Image, ImageOps
import subprocess
from pdf2image import convert_from_path


def compile_latex(tex_file):
    tex_path = Path(tex_file)
    pdf_path = tex_path.with_suffix(".pdf")
    
    subprocess.run([
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory", str(tex_path.parent),
        str(tex_path)
    ], capture_output=True, timeout=25)
    
    return pdf_path if pdf_path.exists() else None


def main():
    tex_file = "example.tex"
    bg_file = "background.jpg"
    output_file = "output_blackboard.png"
    
    if not Path(tex_file).exists() or not Path(bg_file).exists():
        print("Missing example.tex or background.jpg")
        return
    
    pdf_path = compile_latex(tex_file)
    if not pdf_path:
        print("Compilation failed")
        return
    
    # Convert PDF to image
    page = convert_from_path(pdf_path, dpi=400)[0]
    
    # Create clean white chalk effect
    gray = page.convert("L")
    mask = gray.point(lambda x: 0 if x > 225 else 255, mode="1")
    
    chalk = ImageOps.invert(gray)
    chalk = chalk.point(lambda x: min(255, int(x * 1.9)))
    chalk = chalk.convert("RGBA")
    chalk.putalpha(mask)
    
    # Load and prepare background
    background = Image.open(bg_file).convert("RGB")
    
    # Resize chalk to fit nicely
    max_w = int(background.width * 0.88)
    max_h = int(background.height * 0.82)
    chalk.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    
    x = (background.width - chalk.width) // 2
    y = (background.height - chalk.height) // 2
    
    # Paste chalk on background
    background.paste(chalk, (x, y), chalk)
    
    background.save(output_file, quality=98)
    print(f"✅ Saved as {output_file}")
    background.show()


main()
