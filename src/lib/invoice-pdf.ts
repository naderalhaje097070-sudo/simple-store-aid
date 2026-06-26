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
        <td style="padding:7px 5px;border-bottom:1px solid #eee;text-align:center;color:#666;font-size:11px;white-space:nowrap" dir="ltr">${i + 1}</td>
        <td style="padding:7px 5px;border-bottom:1px solid #eee;text-align:right;word-break:break-word">${escape(it.name)}</td>
        <td style="padding:7px 5px;border-bottom:1px solid #eee;text-align:center;white-space:nowrap" dir="ltr">${qty(it.qty)}</td>
        <td style="padding:7px 5px;border-bottom:1px solid #eee;text-align:center;white-space:nowrap" dir="ltr">${money(it.price)}</td>
        <td style="padding:7px 5px;border-bottom:1px solid #eee;text-align:center;font-weight:600;white-space:nowrap" dir="ltr">${money(it.qty * it.price)}</td>
      </tr>`,
    )
    .join("");

  const courierLine =
    d.delivery === "courier"
      ? `<div style="margin-top:4px"><b>المندوب:</b> ${escape(d.courierName ?? "—")}</div>`
      : "";
  const custodyLine =
    (d.collectedByCourier ?? 0) > 0
      ? `<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:5px 0;color:#b45309"><span>بيد المندوب (عهدة)</span><span dir="ltr" style="white-space:nowrap">${money(d.collectedByCourier ?? 0)} د.ل</span></div>`
      : "";

  return `
  <div dir="rtl" style="font-family:${FONT_STACK};color:#111;padding:4px 6px;width:540px;background:#fff;line-height:1.55;box-sizing:border-box">
    <!-- Header -->
    <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px double #111;padding-bottom:10px;margin-bottom:12px;gap:10px">
      <div style="text-align:right;min-width:0;flex:1">
        <div style="font-size:12px;color:#666;font-weight:600;letter-spacing:1px">منجز</div>
        <div style="font-size:20px;font-weight:800;margin-top:2px;word-break:break-word">${escape(d.shopName || "محلي")}</div>
        <div style="font-size:10.5px;color:#777;margin-top:2px">فاتورة بيع غير ضريبية</div>
      </div>
      <div style="text-align:left;background:#111;color:#fff;padding:8px 12px;border-radius:8px;min-width:120px;flex-shrink:0">
        <div style="font-size:9.5px;opacity:.8;font-weight:600">رقم الفاتورة</div>
        <div style="font-size:17px;font-weight:800;margin-top:2px;white-space:nowrap" dir="ltr">#${escape(invNo)}</div>
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
    <table data-pdf="items" style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:12px;border:1px solid #111;border-radius:6px;overflow:hidden">
      <thead>
        <tr style="background:#111;color:#fff">
          <th style="padding:7px 4px;text-align:center;width:22px">#</th>
          <th style="padding:7px 5px;text-align:right">الصنف</th>
          <th style="padding:7px 4px;text-align:center;white-space:nowrap">الكمية</th>
          <th style="padding:7px 6px;text-align:center;white-space:nowrap">السعر</th>
          <th style="padding:7px 6px;text-align:center;white-space:nowrap">الإجمالي</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>

    <!-- Summary (kept together with footer) -->
    <div data-pdf="summary">
      <div style="font-size:12.5px;border:1px solid #111;border-radius:8px;padding:8px 12px;background:#fcfcfc">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:5px 0;font-weight:800;font-size:14.5px;border-bottom:1px solid #ddd;margin-bottom:2px">
          <span>الإجمالي</span><span dir="ltr" style="white-space:nowrap">${money(d.total)} د.ل</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:5px 0;color:#15803d">
          <span>المدفوع للصندوق</span><span dir="ltr" style="white-space:nowrap">${money(d.paid)} د.ل</span>
        </div>
        ${custodyLine}
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:5px 0;font-weight:700;color:${d.remaining > 0 ? "#b91c1c" : "#111"}">
          <span>المتبقي على العميل</span><span dir="ltr" style="white-space:nowrap">${money(d.remaining)} د.ل</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:5px 0;font-size:11.5px;color:#666;border-top:1px dashed #ddd;margin-top:2px">
          <span>طريقة الدفع</span><span>${methodLabel}</span>
        </div>
      </div>

      <!-- Footer -->
      <div style="text-align:center;font-size:11.5px;color:#555;margin-top:14px;border-top:1px dashed #ccc;padding-top:10px">
        شكراً لتعاملكم مع <b>${escape(d.shopName || "محلنا")}</b>
        <div style="margin-top:4px;font-size:10px;color:#999">تم إصدار هذه الفاتورة عبر تطبيق منجز</div>
      </div>
    </div>
  </div>`;
}

function escape(s: string): string {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!,
  );
}

type RenderResult = { canvas: HTMLCanvasElement; breakPoints: number[] };

async function renderToCanvas(d: InvoicePdfData): Promise<RenderResult> {
  await ensureFont();
  // Isolated iframe so the app's oklch CSS tokens don't reach html2canvas.
  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.top = "-10000px";
  iframe.style.left = "0";
  iframe.style.width = "600px";
  iframe.style.height = "1200px";
  iframe.style.border = "0";
  iframe.style.zIndex = "-1";
  document.body.appendChild(iframe);
  try {
    const doc = iframe.contentDocument!;
    doc.open();
    doc.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
      <link rel="stylesheet" href="${FONT_HREF}">
      <style>html,body{margin:0;padding:0;background:#fff;color:#111;font-family:${FONT_STACK}}</style>
      </head><body>${buildHtml(d)}</body></html>`);
    doc.close();
    // @ts-ignore
    if (doc.fonts && doc.fonts.ready) { try { await doc.fonts.ready; } catch {} }
    await new Promise((r) => setTimeout(r, 120));
    const root = doc.body.firstElementChild as HTMLElement;
    const rootRect = root.getBoundingClientRect();

    // Collect break-safe Y boundaries (CSS px, relative to root top):
    //  - top of every <tr> in items table (except the first, which is the header inside thead — kept on first occurrence so summary fits)
    //  - top of the summary block (so summary+footer stay together)
    const breaks = new Set<number>();
    breaks.add(0);
    root.querySelectorAll('table[data-pdf="items"] tbody tr').forEach((tr) => {
      const top = (tr as HTMLElement).getBoundingClientRect().top - rootRect.top;
      breaks.add(Math.round(top));
    });
    const summary = root.querySelector('[data-pdf="summary"]') as HTMLElement | null;
    if (summary) {
      const top = summary.getBoundingClientRect().top - rootRect.top;
      breaks.add(Math.round(top));
    }
    breaks.add(Math.round(root.scrollHeight));

    const canvas = await html2canvas(root, {
      scale: 2,
      backgroundColor: "#ffffff",
      windowWidth: 600,
      windowHeight: Math.max(1200, root.scrollHeight + 40),
    });
    // Scale break points from CSS px → canvas px (html2canvas scale=2)
    const scaleY = canvas.height / root.scrollHeight;
    const breakPoints = Array.from(breaks)
      .map((y) => Math.round(y * scaleY))
      .sort((a, b) => a - b);
    return { canvas, breakPoints };
  } finally {
    document.body.removeChild(iframe);
  }
}

export async function downloadInvoicePdf(d: InvoicePdfData) {
  const { canvas, breakPoints } = await renderToCanvas(d);
  const pdf = new jsPDF({ unit: "mm", format: "a5", orientation: "portrait" });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const wMm = pageW - margin * 2;
  const pageContentHMm = pageH - margin * 2;
  const pxPerMm = canvas.width / wMm;
  const maxSlicePx = Math.floor(pageContentHMm * pxPerMm);

  // Single page fast path
  if (canvas.height <= maxSlicePx) {
    const img = canvas.toDataURL("image/png");
    pdf.addImage(img, "PNG", margin, margin, wMm, canvas.height / pxPerMm);
  } else {
    let y = 0;
    let first = true;
    while (y < canvas.height) {
      // Find the largest break point > y and within (y + maxSlicePx]
      let cut = -1;
      for (const bp of breakPoints) {
        if (bp > y && bp - y <= maxSlicePx) cut = bp;
      }
      // If no safe break fits (a single row taller than a page), hard-cut.
      if (cut === -1) cut = Math.min(y + maxSlicePx, canvas.height);
      const sliceH = cut - y;
      const c2 = document.createElement("canvas");
      c2.width = canvas.width;
      c2.height = sliceH;
      const ctx = c2.getContext("2d")!;
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, c2.width, c2.height);
      ctx.drawImage(canvas, 0, y, canvas.width, sliceH, 0, 0, canvas.width, sliceH);
      if (!first) pdf.addPage();
      first = false;
      pdf.addImage(c2.toDataURL("image/png"), "PNG", margin, margin, wMm, sliceH / pxPerMm);
      y = cut;
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
