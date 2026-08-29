type PdfDocument = {
  addImage: (
    imageData: string,
    format: "PNG",
    x: number,
    y: number,
    width: number,
    height: number
  ) => void;
  addPage: () => void;
  internal: { pageSize: { getHeight: () => number; getWidth: () => number } };
  link: (x: number, y: number, width: number, height: number, options: { url: string }) => void;
  save: (fileName: string) => void;
};

const pageMargin = 12;
const blockGap = 5;

export async function downloadElementAsPdf(element: HTMLElement, fileName: string) {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import("html2canvas"),
    import("jspdf")
  ]);
  const pdf = new jsPDF({ format: "a4", orientation: "portrait", unit: "mm" }) as PdfDocument;
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const contentWidth = pageWidth - pageMargin * 2;
  const contentHeight = pageHeight - pageMargin * 2;
  const blocks = Array.from(element.querySelectorAll<HTMLElement>("[data-pdf-block]"));
  let cursorY = pageMargin;

  for (const block of blocks) {
    const canvas = await html2canvas(block, {
      backgroundColor: "#ffffff",
      scale: 2,
      useCORS: true
    });
    const imageData = canvas.toDataURL("image/png");
    const imageHeight = (canvas.height * contentWidth) / canvas.width;

    if (imageHeight > contentHeight) {
      cursorY = addOversizedBlock(
        pdf,
        imageData,
        imageHeight,
        contentWidth,
        contentHeight,
        pageHeight,
        cursorY
      );
      continue;
    }
    if (cursorY + imageHeight > pageHeight - pageMargin) {
      pdf.addPage();
      cursorY = pageMargin;
    }

    pdf.addImage(imageData, "PNG", pageMargin, cursorY, contentWidth, imageHeight);
    addBlockLinks(pdf, block, contentWidth / block.getBoundingClientRect().width, cursorY);
    cursorY += imageHeight + blockGap;
  }
  pdf.save(fileName);
}

function addOversizedBlock(
  pdf: PdfDocument,
  imageData: string,
  imageHeight: number,
  contentWidth: number,
  contentHeight: number,
  pageHeight: number,
  cursorY: number
) {
  if (cursorY > pageMargin) {
    pdf.addPage();
  }
  let offsetY = pageMargin;
  pdf.addImage(imageData, "PNG", pageMargin, offsetY, contentWidth, imageHeight);
  while (imageHeight + offsetY > pageHeight - pageMargin) {
    offsetY -= contentHeight;
    pdf.addPage();
    pdf.addImage(imageData, "PNG", pageMargin, offsetY, contentWidth, imageHeight);
  }
  return imageHeight + offsetY + blockGap;
}

function addBlockLinks(pdf: PdfDocument, block: HTMLElement, scale: number, blockTop: number) {
  const blockBounds = block.getBoundingClientRect();
  for (const link of Array.from(block.querySelectorAll<HTMLAnchorElement>("a[href]"))) {
    const url = link.href;
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      continue;
    }
    const bounds = link.getBoundingClientRect();
    const x = pageMargin + (bounds.left - blockBounds.left) * scale;
    const y = blockTop + (bounds.top - blockBounds.top) * scale;
    pdf.link(x, y, bounds.width * scale, bounds.height * scale, { url });
  }
}
