export async function downloadElementAsPdf(element: HTMLElement, fileName: string) {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import("html2canvas"),
    import("jspdf")
  ]);
  const canvas = await html2canvas(element, {
    backgroundColor: "#ffffff",
    scale: 2,
    useCORS: true
  });
  const pdf = new jsPDF({ format: "a4", orientation: "portrait", unit: "mm" });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const imageHeight = (canvas.height * pageWidth) / canvas.width;
  const imageData = canvas.toDataURL("image/png");
  let offsetY = 0;

  pdf.addImage(imageData, "PNG", 0, offsetY, pageWidth, imageHeight);
  while (imageHeight + offsetY > pageHeight) {
    offsetY -= pageHeight;
    pdf.addPage();
    pdf.addImage(imageData, "PNG", 0, offsetY, pageWidth, imageHeight);
  }
  pdf.save(fileName);
}
