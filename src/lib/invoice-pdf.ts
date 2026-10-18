import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import QRCode from "qrcode";

export type InvoicePdfData = {
  shopName: string;
  shopPhone?: string;
  shopAddress?: string;
  number: string;
  /** ISO string or Date. If omitted, falls back to dateText/timeText. */
  issuedAt?: string | Date;
  dateText?: string;
  timeText?: string;
  customerName?: string;
  customerPhone?: string;
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

const qty = (n: number) => n.toLocaleString("en-US");

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

function formatInvoiceNumber(raw: string): string {
  const s = String(raw ?? "").trim();
  if (/^\d+$/.test(s)) return s.padStart(5, "0");
  return s;
}

/* ============ Arabic number → words (Libyan Dinar) ============ */
const ONES = [
  "",
  "واحد",
  "اثنان",
  "ثلاثة",
  "أربعة",
  "خمسة",
  "ستة",
  "سبعة",
  "ثمانية",
  "تسعة",
  "عشرة",
  "أحد عشر",
  "اثنا عشر",
  "ثلاثة عشر",
  "أربعة عشر",
  "خمسة عشر",
  "ستة عشر",
  "سبعة عشر",
  "ثمانية عشر",
  "تسعة عشر",
];
const TENS = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"];
const HUNDREDS = [
  "",
  "مئة",
  "مئتان",
  "ثلاثمئة",
  "أربعمئة",
  "خمسمئة",
  "ستمئة",
  "سبعمئة",
  "ثمانمئة",
  "تسعمئة",
];

function under1000(n: number): string {
  if (n === 0) return "";
  const parts: string[] = [];
  const h = Math.floor(n / 100);
  const r = n % 100;
  if (h) parts.push(HUNDREDS[h]);
  if (r) {
    if (r < 20) parts.push(ONES[r]);
    else {
      const t = Math.floor(r / 10);
      const u = r % 10;
      if (u) parts.push(`${ONES[u]} و${TENS[t]}`);
      else parts.push(TENS[t]);
    }
  }
  return parts.join(" و");
}

function intToArabic(n: number): string {
  if (n === 0) return "صفر";
  if (n < 0) return `سالب ${intToArabic(-n)}`;
  const parts: string[] = [];
  const millions = Math.floor(n / 1_000_000);
  const thousands = Math.floor((n % 1_000_000) / 1000);
  const rest = n % 1000;
  if (millions) {
    if (millions === 1) parts.push("مليون");
    else if (millions === 2) parts.push("مليونان");
    else if (millions <= 10) parts.push(`${ONES[millions]} ملايين`);
    else parts.push(`${under1000(millions)} مليون`);
  }
  if (thousands) {
    if (thousands === 1) parts.push("ألف");
    else if (thousands === 2) parts.push("ألفان");
    else if (thousands <= 10) parts.push(`${ONES[thousands]} آلاف`);
    else parts.push(`${under1000(thousands)} ألف`);
  }
  if (rest) parts.push(under1000(rest));
  return parts.join(" و");
}

function amountInWords(amount: number): string {
  const rounded = Math.round((amount + Number.EPSILON) * 100) / 100;
  const dinars = Math.floor(rounded);
  const dirhams = Math.round((rounded - dinars) * 100);
  const dinarPart = `${intToArabic(dinars)} دينار${dinars === 1 ? "" : "ًا ليبيًا"}`;
  if (dirhams === 0) return `فقط: ${dinarPart} لا غير`;
  return `فقط: ${dinarPart} و${intToArabic(dirhams)} درهمًا لا غير`;
}

/* ============ Font loading ============ */
const FONT_HREF =
  "https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap";

const FONT_STACK = "'Cairo', 'Noto Naskh Arabic', 'Segoe UI', Tahoma, Arial, sans-serif";

let fontLoaded: Promise<void> | null = null;
export function ensureFont(): Promise<void> {
  if (fontLoaded) return fontLoaded;
  fontLoaded = new Promise<void>((resolve) => {
    let done = false;
    const finish = () => {
      if (!done) {
        done = true;
        resolve();
      }
    };
    try {
      if (!document.querySelector('link[data-invoice-font="cairo"]')) {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = FONT_HREF;
        link.setAttribute("data-invoice-font", "cairo");
        document.head.appendChild(link);
      }
      // @ts-ignore
      if (document.fonts && document.fonts.load) {
        Promise.all([
          // @ts-ignore
          document.fonts.load('700 16px "Cairo"'),
          // @ts-ignore
          document.fonts.load('400 14px "Cairo"'),
        ])
          .then(finish)
          .catch(finish);
      } else {
        setTimeout(finish, 400);
      }
      // Hard timeout — never block export beyond 2.5s
      setTimeout(() => {
        if (!done) console.warn("[invoice-pdf] font load timed out, using fallback");
        finish();
      }, 2500);
    } catch {
      finish();
    }
  });
  return fontLoaded;
}

/* ============ HTML builder ============ */
function buildHtml(d: InvoicePdfData, qrDataUrl: string | null): string {
  const statusLabel =
    d.status === "paid" ? "مدفوعة" : d.status === "partial" ? "مدفوعة جزئياً" : "آجلة (دين)";
  const statusColor =
    d.status === "paid" ? "#15803d" : d.status === "partial" ? "#b45309" : "#b91c1c";
  const methodLabel = d.method === "cash" ? "نقدي" : d.method === "transfer" ? "تحويل" : "—";

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

  const shopMetaLine = [d.shopPhone, d.shopAddress].filter(Boolean).join(" • ");
  const shopMetaHtml = shopMetaLine
    ? `<div style="font-size:10.5px;color:#666;margin-top:3px" dir="auto">${escape(shopMetaLine)}</div>`
    : "";

  const customerLine = d.customerPhone
    ? `<div><b>العميل:</b> ${escape(d.customerName ?? "بدون عميل")} <span style="color:#666" dir="ltr">— ${escape(d.customerPhone)}</span></div>`
    : `<div><b>العميل:</b> ${escape(d.customerName ?? "بدون عميل")}</div>`;

  const courierLine =
    d.delivery === "courier"
      ? `<div style="margin-top:4px"><b>المندوب:</b> ${escape(d.courierName ?? "—")}</div>`
      : "";

  const custodyLine =
    (d.collectedByCourier ?? 0) > 0
      ? `<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:5px 0;color:#b45309"><span>بيد المندوب (عهدة)</span><span dir="ltr" style="white-space:nowrap">${money(d.collectedByCourier ?? 0)} د.ل</span></div>`
      : "";

  const qrHtml = qrDataUrl
    ? `<img src="${qrDataUrl}" alt="Invoice verification QR code" style="width:72px;height:72px;display:block" />`
    : "";

  return `
  <div dir="rtl" style="font-family:${FONT_STACK};color:#111;padding:4px 6px;width:540px;background:#fff;line-height:1.55;box-sizing:border-box">
    <!-- Header -->
    <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px double #111;padding-bottom:10px;margin-bottom:12px;gap:10px">
      <div style="text-align:right;min-width:0;flex:1">
        <div style="font-size:12px;color:#666;font-weight:600;letter-spacing:1px">منجز</div>
        <div style="font-size:20px;font-weight:800;margin-top:2px;word-break:break-word">${escape(d.shopName || "محلي")}</div>
        ${shopMetaHtml}
        <div style="font-size:10.5px;color:#777;margin-top:3px">فاتورة بيع غير ضريبية</div>
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
      ${customerLine}
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
      <div style="display:flex;gap:10px;align-items:stretch">
        <div style="flex:1;font-size:12.5px;border:1px solid #111;border-radius:8px;padding:8px 12px;background:#fcfcfc">
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
        ${qrHtml ? `<div style="flex-shrink:0;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px solid #ddd;border-radius:8px;padding:6px 8px;background:#fff">${qrHtml}<div style="font-size:9px;color:#999;margin-top:3px">تحقّق</div></div>` : ""}
      </div>

      <!-- Amount in words -->
      <div style="font-size:11.5px;color:#333;margin-top:8px;padding:6px 10px;background:#fafafa;border-right:3px solid #111;border-radius:4px" dir="rtl">
        ${escape(amountInWords(d.total))}
      </div>

      <!-- Footer -->
      <div style="text-align:center;font-size:11.5px;color:#555;margin-top:12px;border-top:1px dashed #ccc;padding-top:10px">
        شكراً لتعاملكم مع <b>${escape(d.shopName || "محلنا")}</b>
        <div style="margin-top:4px;font-size:10px;color:#999">تم إصدار هذه الفاتورة عبر تطبيق منجز</div>
      </div>
    </div>
  </div>`;
}

function escape(s: string): string {
  return String(s ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!,
  );
}

/* ============ QR ============ */
async function buildQr(d: InvoicePdfData): Promise<string | null> {
  try {
    const { date, time } = formatDateTime(d);
    const payload = [
      "منجز",
      `#${formatInvoiceNumber(d.number)}`,
      `${date} ${time}`.trim(),
      `${money(d.total)} د.ل`,
      d.shopName || "",
    ]
      .filter(Boolean)
      .join(" | ");
    return await QRCode.toDataURL(payload, {
      errorCorrectionLevel: "M",
      margin: 1,
      width: 220,
      color: { dark: "#111111", light: "#ffffff" },
    });
  } catch (e) {
    console.warn("[invoice-pdf] QR failed:", e);
    return null;
  }
}

/* ============ Render ============ */
type RenderResult = { canvas: HTMLCanvasElement; breakPoints: number[] };

async function renderToCanvas(d: InvoicePdfData): Promise<RenderResult> {
  await ensureFont();
  const qrDataUrl = await buildQr(d);
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
      </head><body>${buildHtml(d, qrDataUrl)}</body></html>`);
    doc.close();
    // @ts-ignore
    if (doc.fonts && doc.fonts.ready) {
      try {
        await doc.fonts.ready;
      } catch {}
    }
    await new Promise((r) => setTimeout(r, 120));
    const root = doc.body.firstElementChild as HTMLElement;
    const rootRect = root.getBoundingClientRect();

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

    const scale = Math.min(3, Math.max(2, Math.round((window.devicePixelRatio || 1) * 2)));
    const canvas = await html2canvas(root, {
      scale,
      backgroundColor: "#ffffff",
      windowWidth: 600,
      windowHeight: Math.max(1200, root.scrollHeight + 40),
    });
    const scaleY = canvas.height / root.scrollHeight;
    const breakPoints = Array.from(breaks)
      .map((y) => Math.round(y * scaleY))
      .sort((a, b) => a - b);
    return { canvas, breakPoints };
  } finally {
    document.body.removeChild(iframe);
  }
}

function safeFilename(shop: string, invNo: string): string {
  // Keep latin letters/digits/hyphens only — Arabic chars often break Save dialogs.
  const ascii = shop
    .normalize("NFKD")
    .replace(/[\u0600-\u06FF]/g, "")
    .replace(/[^A-Za-z0-9-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase();
  const base = ascii || "mongezz";
  return `${base}-invoice-${invNo}.pdf`;
}

export async function downloadInvoicePdf(d: InvoicePdfData) {
  const { canvas, breakPoints } = await renderToCanvas(d);
  const pdf = new jsPDF({ unit: "mm", format: "a5", orientation: "portrait", compress: true });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const wMm = pageW - margin * 2;
  const pageContentHMm = pageH - margin * 2 - 6; // reserve 6mm for page number footer
  const pxPerMm = canvas.width / wMm;
  const maxSlicePx = Math.floor(pageContentHMm * pxPerMm);

  const addSlice = (y: number, sliceH: number) => {
    const c2 = document.createElement("canvas");
    c2.width = canvas.width;
    c2.height = sliceH;
    const ctx = c2.getContext("2d")!;
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, c2.width, c2.height);
    ctx.drawImage(canvas, 0, y, canvas.width, sliceH, 0, 0, canvas.width, sliceH);
    pdf.addImage(c2.toDataURL("image/jpeg", 0.92), "JPEG", margin, margin, wMm, sliceH / pxPerMm);
  };

  if (canvas.height <= maxSlicePx) {
    addSlice(0, canvas.height);
  } else {
    let y = 0;
    let first = true;
    while (y < canvas.height) {
      let cut = -1;
      for (const bp of breakPoints) {
        if (bp > y && bp - y <= maxSlicePx) cut = bp;
      }
      if (cut === -1) cut = Math.min(y + maxSlicePx, canvas.height);
      const sliceH = cut - y;
      if (!first) pdf.addPage();
      first = false;
      addSlice(y, sliceH);
      y = cut;
    }
  }

  // Page numbers (LTR — jsPDF default font is latin-only)
  const total = pdf.getNumberOfPages();
  if (total > 1) {
    for (let i = 1; i <= total; i++) {
      pdf.setPage(i);
      pdf.setFontSize(8);
      pdf.setTextColor(140);
      pdf.text(`Page ${i} / ${total}`, pageW / 2, pageH - 4, { align: "center" });
    }
  }

  const invNo = formatInvoiceNumber(d.number);
  pdf.save(safeFilename(d.shopName || "mongezz", invNo));
}

export function printInvoice(d: InvoicePdfData) {
  const w = window.open("", "_blank", "width=600,height=800");
  if (!w) return;
  const invNo = formatInvoiceNumber(d.number);
  // Build with a transient QR to keep print parity with PDF
  buildQr(d).then((qrDataUrl) => {
    const html = buildHtml(d, qrDataUrl);
    w.document.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
      <title>فاتورة #${invNo} — ${escape(d.shopName || "منجز")}</title>
      <link rel="stylesheet" href="${FONT_HREF}">
      <style>
        @page { size: A5; margin: 8mm; }
        html, body { margin:0; font-family: ${FONT_STACK}; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        [data-pdf="summary"] { page-break-inside: avoid; break-inside: avoid; }
        table[data-pdf="items"] tr { page-break-inside: avoid; break-inside: avoid; }
      </style>
      </head><body>${html}<script>window.onload=()=>{setTimeout(()=>{window.print();},500);};</script></body></html>`);
    w.document.close();
  });
}
