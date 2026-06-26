import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export type InvoicePdfData = {
  shopName: string;
  number: string;
  /** ISO string or Date. If omitted, falls back to dateText/timeText. */
  issuedAt?: string | Date;
  dateText?: string;
  timeText?: string;
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

// Money: thousands separator, 2 decimals, LTR. e.g. 1,250.00
const money = (n: number) =>
  (Math.round((n + Number.EPSILON) * 100) / 100).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

// Integer qty
const qty = (n: number) => n.toLocaleString("en-US");

// Date: dd/MM/yyyy - HH:mm (LTR)
function formatDateTime(d: InvoicePdfData): { date: string; time: string } {
  let dt: Date | null = null;
  if (d.issuedAt) dt = d.issuedAt instanceof Date ? d.issuedAt : new Date(d.issuedAt);
  if (dt && !isNaN(dt.getTime())) {
    const pad = (n: number) => String(n).padStart(2, "0");
    const date = `${pad(dt.getDate())}/${pad(dt.getMonth() + 1)}/${dt.getFullYear()}`;
    const time = `${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
    return { date, time };
  }
  return { date: d.dateText ?? "", time: d.timeText ?? "" };
}

// Pad invoice number to a clean fixed width when numeric
function formatInvoiceNumber(raw: string): string {
  const s = String(raw ?? "").trim();
  if (/^\d+$/.test(s)) return s.padStart(5, "0");
  return s;
}

const FONT_HREF =
  "https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap";

const FONT_STACK =
  "'Cairo', 'Noto Naskh Arabic', 'Segoe UI', Tahoma, Arial, sans-serif";

let fontLoaded: Promise<void> | null = null;
function ensureFont(): Promise<void> {
  if (fontLoaded) return fontLoaded;
  fontLoaded = new Promise<void>((resolve) => {
    try {
      if (!document.querySelector('link[data-invoice-font="cairo"]')) {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = FONT_HREF;
        link.setAttribute("data-invoice-font", "cairo");
        document.head.appendChild(link);
      }
      const done = () => resolve();
      // @ts-ignore
      if (document.fonts && document.fonts.load) {
        Promise.all([
          // @ts-ignore
          document.fonts.load('700 16px "Cairo"'),
          // @ts-ignore
          document.fonts.load('400 14px "Cairo"'),
        ])
          .then(done)
          .catch(done);
      } else {
        setTimeout(done, 400);
      }
    } catch {
      resolve();
    }
  });
  return fontLoaded;
}

function buildHtml(d: InvoicePdfData): string {
  const statusLabel =
    d.status === "paid" ? "مدفوعة" : d.status === "partial" ? "مدفوعة جزئياً" : "آجلة (دين)";
  const statusColor =
    d.status === "paid" ? "#15803d" : d.status === "partial" ? "#b45309" : "#b91c1c";
  const methodLabel =
    d.method === "cash" ? "نقدي" : d.method === "transfer" ? "تحويل" : "—";

  const { date, time } = formatDateTime(d);
  const invNo = formatInvoiceNumber(d.number);

  const rows = d.items
    .map(
      (it, i) => `
      <tr style="background:${i % 2 ? "#fafafa" : "#fff"}">
        <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:center;color:#666;font-size:11px" dir="ltr">${i + 1}</td>
        <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:right">${escape(it.name)}</td>
        <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:center" dir="ltr">${qty(it.qty)}</td>
        <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:center" dir="ltr">${money(it.price)}</td>
        <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:center;font-weight:600" dir="ltr">${money(it.qty * it.price)}</td>
      </tr>`,
    )
    .join("");

  const courierLine =
    d.delivery === "courier"
      ? `<div style="margin-top:4px"><b>المندوب:</b> ${escape(d.courierName ?? "—")}</div>`
      : "";
  const custodyLine =
    (d.collectedByCourier ?? 0) > 0
      ? `<div style="display:flex;justify-content:space-between;padding:6px 0;color:#b45309"><span>بيد المندوب (عهدة)</span><span dir="ltr">${money(d.collectedByCourier ?? 0)} د.ل</span></div>`
      : "";

  return `
  <div dir="rtl" style="font-family:${FONT_STACK};color:#111;padding:20px;width:560px;background:#fff;line-height:1.6">
    <!-- Header -->
    <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px double #111;padding-bottom:12px;margin-bottom:14px">
      <div style="text-align:right">
        <div style="font-size:13px;color:#666;font-weight:600;letter-spacing:1px">منجز</div>
        <div style="font-size:22px;font-weight:800;margin-top:2px">${escape(d.shopName || "محلي")}</div>
        <div style="font-size:11px;color:#777;margin-top:2px">فاتورة بيع غير ضريبية</div>
      </div>
      <div style="text-align:left;background:#111;color:#fff;padding:10px 14px;border-radius:8px;min-width:130px">
        <div style="font-size:10px;opacity:.8;font-weight:600">رقم الفاتورة</div>
        <div style="font-size:18px;font-weight:800;margin-top:2px" dir="ltr">#${escape(invNo)}</div>
      </div>
    </div>

    <!-- Meta -->
    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:10px;color:#333">
      <div><b>التاريخ:</b> <span dir="ltr">${escape(date)}</span></div>
      <div><b>الوقت:</b> <span dir="ltr">${escape(time)}</span></div>
      <div><b>الحالة:</b> <span style="color:${statusColor};font-weight:700">${statusLabel}</span></div>
    </div>

    <!-- Parties -->
    <div style="font-size:12.5px;background:#f7f7f7;padding:10px 12px;border-radius:8px;margin-bottom:12px;border:1px solid #eee">
      <div><b>العميل:</b> ${escape(d.customerName ?? "بدون عميل")}</div>
      ${courierLine}
    </div>

    <!-- Items -->
    <table style="width:100%;border-collapse:collapse;font-size:12.5px;margin-bottom:12px;border:1px solid #111;border-radius:6px;overflow:hidden">
      <thead>
        <tr style="background:#111;color:#fff">
          <th style="padding:8px 6px;text-align:center;width:30px">#</th>
          <th style="padding:8px 6px;text-align:right">الصنف</th>
          <th style="padding:8px 6px;text-align:center;width:60px">الكمية</th>
          <th style="padding:8px 6px;text-align:center;width:80px">السعر</th>
          <th style="padding:8px 6px;text-align:center;width:90px">الإجمالي</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>

    <!-- Summary -->
    <div style="font-size:13px;border:1px solid #111;border-radius:8px;padding:10px 12px;background:#fcfcfc">
      <div style="display:flex;justify-content:space-between;padding:6px 0;font-weight:800;font-size:15px;border-bottom:1px solid #ddd;margin-bottom:4px">
        <span>الإجمالي</span><span dir="ltr">${money(d.total)} د.ل</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:6px 0;color:#15803d">
        <span>المدفوع للصندوق</span><span dir="ltr">${money(d.paid)} د.ل</span>
      </div>
      ${custodyLine}
      <div style="display:flex;justify-content:space-between;padding:6px 0;font-weight:700;color:${d.remaining > 0 ? "#b91c1c" : "#111"}">
        <span>المتبقي على العميل</span><span dir="ltr">${money(d.remaining)} د.ل</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:12px;color:#666;border-top:1px dashed #ddd;margin-top:4px">
        <span>طريقة الدفع</span><span>${methodLabel}</span>
      </div>
    </div>

    <!-- Footer -->
    <div style="text-align:center;font-size:11.5px;color:#555;margin-top:18px;border-top:1px dashed #ccc;padding-top:12px">
      شكراً لتعاملكم مع <b>${escape(d.shopName || "محلنا")}</b> 🌿
      <div style="margin-top:4px;font-size:10px;color:#999">تم إصدار هذه الفاتورة عبر تطبيق منجز</div>
    </div>
  </div>`;
}

function escape(s: string): string {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!,
  );
}

async function renderToCanvas(d: InvoicePdfData) {
  await ensureFont();
  const host = document.createElement("div");
  host.style.position = "fixed";
  host.style.top = "-10000px";
  host.style.left = "0";
  host.style.zIndex = "-1";
  host.innerHTML = buildHtml(d);
  document.body.appendChild(host);
  try {
    const node = host.firstElementChild as HTMLElement;
    // Small delay to ensure webfont applied to nodes
    await new Promise((r) => setTimeout(r, 60));
    const canvas = await html2canvas(node, { scale: 2, backgroundColor: "#ffffff" });
    return canvas;
  } finally {
    document.body.removeChild(host);
  }
}

export async function downloadInvoicePdf(d: InvoicePdfData) {
  const canvas = await renderToCanvas(d);
  const img = canvas.toDataURL("image/png");
  const pdf = new jsPDF({ unit: "mm", format: "a5", orientation: "portrait" });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const margin = 8;
  const w = pageW - margin * 2;
  const h = (canvas.height * w) / canvas.width;
  if (h <= pageH - margin * 2) {
    pdf.addImage(img, "PNG", margin, margin, w, h);
  } else {
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
      pdf.addImage(partImg, "PNG", margin, margin, w, sliceH / pxPerMm);
      y += sliceH;
    }
  }
  const invNo = formatInvoiceNumber(d.number);
  const safeShop = (d.shopName || "mongezz").replace(/[^\w\u0600-\u06FF-]+/g, "_");
  pdf.save(`${safeShop}-invoice-${invNo}.pdf`);
}

export function printInvoice(d: InvoicePdfData) {
  const html = buildHtml(d);
  const w = window.open("", "_blank", "width=600,height=800");
  if (!w) return;
  const invNo = formatInvoiceNumber(d.number);
  w.document.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
    <title>فاتورة #${invNo} — ${escape(d.shopName || "منجز")}</title>
    <link rel="stylesheet" href="${FONT_HREF}">
    <style>
      @page { size: A5; margin: 8mm; }
      body { margin:0; font-family: ${FONT_STACK}; }
    </style>
    </head><body>${html}<script>window.onload=()=>{setTimeout(()=>{window.print();},400);};</script></body></html>`);
  w.document.close();
}
