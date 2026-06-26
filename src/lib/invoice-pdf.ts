import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export type InvoicePdfData = {
  shopName: string;
  number: string;
  dateText: string;
  timeText: string;
  customerName?: string;
  courierName?: string;
  delivery: "direct" | "courier";
  items: { name: string; qty: number; price: number }[];
  total: number;
  paid: number;
  collectedByCourier?: number;
  remaining: number;
  method?: "cash" | "transfer";
  status: "paid" | "partial" | "debt";
};

const fmt = (n: number) =>
  Math.round(n).toLocaleString("en-US");

function buildHtml(d: InvoicePdfData): string {
  const statusLabel =
    d.status === "paid" ? "مدفوعة" : d.status === "partial" ? "مدفوعة جزئياً" : "دين";
  const methodLabel =
    d.method === "cash" ? "نقدي" : d.method === "transfer" ? "تحويل" : "—";
  const rows = d.items
    .map(
      (it) => `
      <tr>
        <td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:right">${escape(it.name)}</td>
        <td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:center" dir="ltr">${it.qty}</td>
        <td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:center" dir="ltr">${fmt(it.price)}</td>
        <td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:center" dir="ltr">${fmt(it.qty * it.price)}</td>
      </tr>`,
    )
    .join("");

  const courierLine =
    d.delivery === "courier"
      ? `<div style="margin-top:2px"><b>المندوب:</b> ${escape(d.courierName ?? "—")}</div>`
      : "";
  const custodyLine =
    (d.collectedByCourier ?? 0) > 0
      ? `<div style="display:flex;justify-content:space-between;padding:4px 0"><span>بيد المندوب (عهدة)</span><span dir="ltr">${fmt(d.collectedByCourier ?? 0)} د.ل</span></div>`
      : "";

  return `
  <div dir="rtl" style="font-family: Tahoma, Arial, sans-serif; color:#111; padding:16px; width:520px; background:#fff;">
    <div style="text-align:center;border-bottom:2px solid #111;padding-bottom:10px;margin-bottom:10px">
      <div style="font-size:20px;font-weight:bold">${escape(d.shopName || "محلي")}</div>
      <div style="font-size:11px;color:#555;margin-top:4px">فاتورة بيع غير ضريبية</div>
    </div>

    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">
      <div><b>رقم الفاتورة:</b> <span dir="ltr">#${escape(d.number)}</span></div>
      <div><b>التاريخ:</b> <span dir="ltr">${escape(d.dateText)} ${escape(d.timeText)}</span></div>
    </div>

    <div style="font-size:12px;background:#f7f7f7;padding:8px;border-radius:6px;margin-bottom:10px">
      <div><b>العميل:</b> ${escape(d.customerName ?? "بدون عميل")}</div>
      ${courierLine}
    </div>

    <table style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:10px">
      <thead>
        <tr style="background:#111;color:#fff">
          <th style="padding:6px 4px;text-align:right">الصنف</th>
          <th style="padding:6px 4px;text-align:center">الكمية</th>
          <th style="padding:6px 4px;text-align:center">السعر</th>
          <th style="padding:6px 4px;text-align:center">الإجمالي</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>

    <div style="font-size:13px;border-top:2px solid #111;padding-top:8px">
      <div style="display:flex;justify-content:space-between;padding:4px 0;font-weight:bold">
        <span>الإجمالي</span><span dir="ltr">${fmt(d.total)} د.ل</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:4px 0">
        <span>المدفوع للصندوق</span><span dir="ltr">${fmt(d.paid)} د.ل</span>
      </div>
      ${custodyLine}
      <div style="display:flex;justify-content:space-between;padding:4px 0;color:${d.remaining > 0 ? "#b91c1c" : "#111"}">
        <span>المتبقي على العميل</span><span dir="ltr">${fmt(d.remaining)} د.ل</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:4px 0;font-size:12px;color:#555">
        <span>طريقة الدفع</span><span>${methodLabel}</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:4px 0;font-size:12px;color:#555">
        <span>الحالة</span><span>${statusLabel}</span>
      </div>
    </div>

    <div style="text-align:center;font-size:11px;color:#555;margin-top:16px;border-top:1px dashed #ccc;padding-top:10px">
      شكراً لتعاملكم مع ${escape(d.shopName || "محلنا")} 🌿
    </div>
  </div>`;
}

function escape(s: string): string {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!,
  );
}

async function renderToCanvas(d: InvoicePdfData) {
  const host = document.createElement("div");
  host.style.position = "fixed";
  host.style.top = "-10000px";
  host.style.left = "0";
  host.style.zIndex = "-1";
  host.innerHTML = buildHtml(d);
  document.body.appendChild(host);
  try {
    const node = host.firstElementChild as HTMLElement;
    const canvas = await html2canvas(node, { scale: 2, backgroundColor: "#ffffff" });
    return canvas;
  } finally {
    document.body.removeChild(host);
  }
}

export async function downloadInvoicePdf(d: InvoicePdfData) {
  const canvas = await renderToCanvas(d);
  const img = canvas.toDataURL("image/png");
  // A5 portrait: 148 x 210 mm
  const pdf = new jsPDF({ unit: "mm", format: "a5", orientation: "portrait" });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const margin = 8;
  const w = pageW - margin * 2;
  const h = (canvas.height * w) / canvas.width;
  if (h <= pageH - margin * 2) {
    pdf.addImage(img, "PNG", margin, margin, w, h);
  } else {
    // split into pages if very long
    const pageContentH = pageH - margin * 2;
    const pxPerMm = canvas.width / w;
    const sliceHeightPx = pageContentH * pxPerMm;
    let y = 0;
    while (y < canvas.height) {
      const sliceH = Math.min(sliceHeightPx, canvas.height - y);
      const c2 = document.createElement("canvas");
      c2.width = canvas.width;
      c2.height = sliceH;
      const ctx = c2.getContext("2d")!;
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, c2.width, c2.height);
      ctx.drawImage(canvas, 0, y, canvas.width, sliceH, 0, 0, canvas.width, sliceH);
      const partImg = c2.toDataURL("image/png");
      if (y > 0) pdf.addPage();
      pdf.addImage(partImg, "PNG", margin, margin, w, (sliceH / pxPerMm));
      y += sliceH;
    }
  }
  pdf.save(`invoice-${d.number}.pdf`);
}

export function printInvoice(d: InvoicePdfData) {
  const html = buildHtml(d);
  const w = window.open("", "_blank", "width=600,height=800");
  if (!w) return;
  w.document.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>فاتورة ${d.number}</title>
    <style>@page { size: A5; margin: 8mm; } body { margin:0; }</style>
    </head><body>${html}<script>window.onload=()=>{setTimeout(()=>{window.print();},150);};</script></body></html>`);
  w.document.close();
}
