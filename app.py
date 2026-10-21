import io
import urllib.parse
from datetime import date
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Diyetisyen Sevgi Topçu", page_icon="🥗", layout="wide")

GREEN = colors.HexColor("#245C49")
PALE = colors.HexColor("#EDF5EF")
INK = colors.HexColor("#24352C")
MUTED = colors.HexColor("#6B7A71")
LINE = colors.HexColor("#DCE5DF")

MEALS = [
    ("Kahvaltı", "08:00"),
    ("Ara Öğün", "10:30"),
    ("Öğle Yemeği", "13:00"),
    ("Ara Öğün", "15:30"),
    ("Akşam Yemeği", "19:00"),
    ("Ara Öğün", "21:00"),
]

def register_turkish_font():
    """Try common font paths; fall back to built-in font if unavailable."""
    candidates = [
        ("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("Arial", "C:/Windows/Fonts/arial.ttf"),
        ("Arial", "/Library/Fonts/Arial.ttf"),
    ]
    for name, path in candidates:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception:
            pass
    return "Helvetica"

def safe_text(value):
    value = (value or "").strip()
    if not value:
        return "Belirtilmedi"
    return value

def build_pdf(client, dietitian, program_date, logo_bytes, meal_data, notes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=17*mm, leftMargin=17*mm,
        topMargin=14*mm, bottomMargin=15*mm,
        title="Diyet Programı",
        author=dietitian or "Diyetisyen"
    )
    font_name = register_turkish_font()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Brand", fontName=font_name, fontSize=8, leading=10,
        textColor=GREEN, alignment=TA_CENTER, spaceAfter=3,
        uppercase=True, tracking=1.2
    ))
    styles.add(ParagraphStyle(
        name="MainTitleTR", fontName=font_name, fontSize=21, leading=25,
        textColor=INK, alignment=TA_CENTER, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="SubtitleTR", fontName=font_name, fontSize=9, leading=12,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name="MetaLabelTR", fontName=font_name, fontSize=7, leading=9,
        textColor=MUTED, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="MetaValueTR", fontName=font_name, fontSize=9, leading=12,
        textColor=INK
    ))
    styles.add(ParagraphStyle(
        name="MealTitleTR", fontName=font_name, fontSize=10, leading=13,
        textColor=GREEN, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="BodyTR", fontName=font_name, fontSize=9, leading=13,
        textColor=INK
    ))
    styles.add(ParagraphStyle(
        name="TimeTR", fontName=font_name, fontSize=9, leading=12,
        textColor=GREEN, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name="NotesTitleTR", fontName=font_name, fontSize=9, leading=12,
        textColor=GREEN, spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="FooterTR", fontName=font_name, fontSize=7, leading=9,
        textColor=MUTED, alignment=TA_CENTER
    ))

    story = []
    if logo_bytes:
        try:
            logo = Image(io.BytesIO(logo_bytes))
            max_w, max_h = 38*mm, 22*mm
            scale = min(max_w / logo.imageWidth, max_h / logo.imageHeight, 1)
            logo.drawWidth = logo.imageWidth * scale
            logo.drawHeight = logo.imageHeight * scale
            logo.hAlign = "CENTER"
            story += [logo, Spacer(1, 3*mm)]
        except Exception:
            story += [Paragraph("DİYETİSYEN BESLENME PLANI", styles["Brand"])]
    else:
        story += [Paragraph("BESLENME PLANI", styles["Brand"])]

    story += [
        Paragraph("DİYET PROGRAMI", styles["MainTitleTR"]),
        Paragraph("Danışana özel günlük beslenme programı", styles["SubtitleTR"]),
    ]

    meta_data = [
        [
            [Paragraph("DANIŞAN", styles["MetaLabelTR"]),
             Paragraph(safe_text(client).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["MetaValueTR"])],
            [Paragraph("DİYETİSYEN", styles["MetaLabelTR"]),
             Paragraph(safe_text(dietitian).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["MetaValueTR"])],
        ],
        [
            [Paragraph("PROGRAM TARİHİ", styles["MetaLabelTR"]),
             Paragraph(program_date.strftime("%d.%m.%Y"), styles["MetaValueTR"])],
            [Paragraph("ÖĞÜN SAYISI", styles["MetaLabelTR"]),
             Paragraph("6 öğün", styles["MetaValueTR"])],
        ]
    ]
    meta_table = Table(meta_data, colWidths=[(A4[0]-34*mm)/2]*2)
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F3F7F4")),
        ("BOX", (0,0), (-1,-1), 0.5, LINE),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 9),
        ("RIGHTPADDING", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story += [meta_table, Spacer(1, 5*mm)]

    for idx, (name, time, content) in enumerate(meal_data, start=1):
        clean_content = (content or "").strip()
        if not clean_content:
            clean_content = "Bu öğün için içerik girilmedi."
        clean_content = (clean_content.replace("&", "&amp;")
                         .replace("<", "&lt;").replace(">", "&gt;")
                         .replace("\n", "<br/>"))
        safe_time = (time or "").strip() or "--:--"
        left = Paragraph(f"<b>{safe_time}</b>", styles["TimeTR"])
        right = [
            Paragraph(f"{idx}. {name}", styles["MealTitleTR"]),
            Paragraph(clean_content, styles["BodyTR"])
        ]
        row = Table([[left, right]], colWidths=[22*mm, A4[0]-34*mm-22*mm])
        row.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (0,0), PALE),
            ("BOX", (0,0), (0,0), 0.4, LINE),
            ("LINEBELOW", (1,0), (1,0), 0.45, LINE),
            ("LEFTPADDING", (0,0), (-1,-1), 7),
            ("RIGHTPADDING", (0,0), (-1,-1), 7),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ]))
        story += [KeepTogether([row, Spacer(1, 1.5*mm)])]

    story += [
        Spacer(1, 4*mm),
        Paragraph("GENEL NOTLAR", styles["NotesTitleTR"]),
    ]
    clean_notes = (notes or "").strip() or "Not eklenmedi."
    clean_notes = (clean_notes.replace("&", "&amp;").replace("<", "&lt;")
                   .replace(">", "&gt;").replace("\n", "<br/>"))
    note_table = Table([[Paragraph(clean_notes, styles["BodyTR"])]], colWidths=[A4[0]-34*mm])
    note_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F5F8F6")),
        ("BOX", (0,0), (-1,-1), 0.5, LINE),
        ("LINEBEFORE", (0,0), (0,0), 3, GREEN),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
    ]))
    story += [note_table, Spacer(1, 8*mm),
              Paragraph("Kişiye özel beslenme programı · Sorularınız için diyetisyeninizle iletişime geçiniz.", styles["FooterTR"])]

    doc.build(story)
    return buffer.getvalue()

st.title("🥗 Diyetisyen Sevgi Topçi")
st.caption("Altı öğünlü programınızı hazırlayın, önizleyin ve PDF olarak indirin.")
st.info("Gizlilik notu: Bu Streamlit sürümünde form verileri PDF oluşturulurken uygulamanın çalıştığı sunucuya iletilir. Uygulama bu kodda bilgileri veritabanına kaydetmez. Hassas danışan bilgilerini girmeden önce barındırma ve gizlilik koşullarını değerlendirmeniz gerekir.")

with st.form("diet_form", clear_on_submit=False):
    st.subheader("Danışan bilgileri")
    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Danışan adı soyadı")
    with col2:
        dietitian = st.text_input("Diyetisyen adı")
    program_date = st.date_input("Program tarihi", value=date.today())

    st.subheader("Logo")
    logo_file = st.file_uploader("Logo dosyası ekleyin (PNG veya JPG)", type=["png", "jpg", "jpeg"])
    if logo_file:
        st.image(logo_file, caption="PDF'de kullanılacak logo", width=170)

    st.subheader("Öğün planı")
    meal_data = []
    for i, (meal_name, default_time) in enumerate(MEALS):
        st.markdown(f"**{i+1}. {meal_name}**")
        time_col, content_col = st.columns([1, 3])
        with time_col:
            time_value = st.text_input("Saat", value=default_time, key=f"time_{i}", placeholder="08:00")
        with content_col:
            content_value = st.text_area("Öğün içeriği", key=f"content_{i}", height=90, placeholder="Besinleri ve açıklamaları buraya yazın...")
        meal_data.append((meal_name, time_value, content_value))

    st.subheader("Genel notlar")
    notes = st.text_area("Danışana özel notlar", height=110, placeholder="Hatırlatmalar ve öneriler...")
    submitted = st.form_submit_button("PDF oluştur", type="primary", use_container_width=True)

if submitted:
    logo_bytes = logo_file.getvalue() if logo_file else None
    try:
        pdf_bytes = build_pdf(client, dietitian, program_date, logo_bytes, meal_data, notes)
        safe_name = "".join(c for c in (client.strip() or "danisan") if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        st.success("PDF hazır. İndirdikten sonra telefonunuzdan paylaşabilirsiniz.")
        st.download_button(
            "PDF'yi indir",
            data=pdf_bytes,
            file_name=f"Diyet_Programi_{safe_name or 'danisan'}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.subheader("PDF önizlemesi")
        st.caption("Önizleme PDF görüntüleyicinizde açılabilir; indirme düğmesi dosyayı cihazınıza kaydeder.")
        st.download_button("PDF'yi tekrar indir", data=pdf_bytes,
                           file_name=f"Diyet_Programi_{safe_name or 'danisan'}.pdf",
                           mime="application/pdf")
    except Exception as exc:
        st.error(f"PDF oluşturulurken bir sorun oluştu: {exc}")
st.divider() # Araya şık bir çizgi çeker
st.subheader("📱 WhatsApp ile Danışana Gönder")

# Telefon numarası ve mesaj alanları
col1, col2 = st.columns(2)
with col1:
    telefon = st.text_input("Danışanın Telefonu (Örn: 5551234567)")
with col2:
    mesaj = st.text_area("Mesajınız", "Merhaba! Bu haftaki diyet listenizi hazırladım. İndirdiğim PDF dosyasını bu mesaja ekleyerek iletiyorum. İyi haftalar! 🍏")

# Telefon numarası girildiyse WhatsApp butonunu göster
if telefon:
    # Numarayı WhatsApp'ın anlayacağı formata çeviriyoruz (Boşlukları sil, başına 90 ekle)
    temiz_no = telefon.replace(" ", "").replace("+", "").replace("-", "")
    if not temiz_no.startswith("90"):
        temiz_no = "90" + temiz_no
        
    # Mesajı linke uygun hale getiriyoruz
    url_mesaj = urllib.parse.quote(mesaj)
    wa_link = f"https://wa.me/{temiz_no}?text={url_mesaj}"
    
    # Yeşil WhatsApp butonu
    st.link_button("🟢 WhatsApp'ta Sohbeti Aç", wa_link)
