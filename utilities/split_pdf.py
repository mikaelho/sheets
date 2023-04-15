import sys
from pathlib import Path

from pypdf import PdfReader
from pypdf import PdfWriter


if len(sys.argv) != 3:
    print("Usage: input_file output_directory (created if does not exist)")
else:
    input_file, output_dir = sys.argv[1:]
    reader = PdfReader(input_file)

    Path(output_dir).mkdir(exist_ok=True)

    for page_no, page in enumerate(reader.pages):
        with PdfWriter() as writer:
            writer.add_page(page)
            # with open(, "wb") as output:
            writer.write(f"{output_dir}/page{page_no:03}.pdf")
