from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPDF
from pathlib import Path

d = Drawing(100, 100)
s = String(50, 50, "Hello, world!", textAnchor="middle")

d.add(s)

path = Path(__file__).resolve().parent
renderPDF.drawToFile(d, path.joinpath("hello.pdf"), "A simple PDF file")
