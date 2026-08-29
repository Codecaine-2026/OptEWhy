import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

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
  output: (type: "blob") => Blob;
};

const pageMargin = 12;
const blockGap = 5;

export async function downloadElementAsPdf(element: HTMLElement, fileName: string) {
  await waitForReportImages(element);
  const pdf = new jsPDF({ format: "a4", orientation: "portrait", unit: "mm" }) as PdfDocument;
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const contentWidth = pageWidth - pageMargin * 2;
  const contentHeight = pageHeight - pageMargin * 2;
  const blocks = Array.from(element.querySelectorAll<HTMLElement>("[data-pdf-block]"));
  let cursorY = pageMargin;

  for (const [index, block] of blocks.entries()) {
    let canvas: HTMLCanvasElement;
    try {
      canvas = await html2canvas(block, {
        backgroundColor: "#ffffff",
        scale: 2,
        useCORS: true,
        logging: false
      });
    } catch (error) {
      throw new Error(`Could not render PDF section ${index + 1} (${getBlockName(block)}): ${formatError(error)}`);
    }

    let imageData: string;
    try {
      imageData = canvas.toDataURL("image/png");
    } catch (error) {
      throw new Error(`Could not encode PDF section ${index + 1} (${getBlockName(block)}): ${formatError(error)}`);
    }
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
  let pdfBlob: Blob;
  try {
    pdfBlob = pdf.output("blob");
  } catch (error) {
    throw new Error(`Could not finalize the PDF: ${formatError(error)}`);
  }
  const downloadUrl = URL.createObjectURL(pdfBlob);
  const downloadLink = document.createElement("a");
  downloadLink.href = downloadUrl;
  downloadLink.download = fileName;
  document.body.append(downloadLink);
  downloadLink.click();
  downloadLink.remove();
  window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 0);
}

async function waitForReportImages(element: HTMLElement) {
  const images = Array.from(element.querySelectorAll<HTMLImageElement>("img"));
  await Promise.all(
    images.map((image) => {
      if (image.complete) {
        return Promise.resolve();
      }
      return new Promise<void>((resolve, reject) => {
        image.addEventListener("load", () => resolve(), { once: true });
        image.addEventListener("error", () => reject(new Error(`Image could not load: ${image.currentSrc || image.src}`)), {
          once: true
        });
      });
    })
  );
}

function getBlockName(block: HTMLElement) {
  return block.querySelector("h1, h2, h3, .reportSectionLabel")?.textContent?.trim() || "report content";
}

function formatError(error: unknown) {
  if (error instanceof Error && error.message) {
    return error.message;
  }
  if (typeof error === "string" && error) {
    return error;
  }
  return "Unknown rendering error";
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
