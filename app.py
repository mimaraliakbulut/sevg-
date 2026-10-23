
import io
import os
from datetime import date
from xml.sax.saxutils import escape

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as PDFImage, KeepTogether
)

# =========================================================
# SAYFA AYARLARI
# =========================================================

st.set_page_config(
    page_title="Diyetisyen Sevgi Akbulut",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

GREEN = "#557563"
DARK_GREEN = "#304E40"
LIGHT_GREEN = "#EAF0EB"
CREAM = "#F7F6F1"
TEXT = "#28342D"
MUTED = "#778178"
BORDER = "#E2E7E0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');

.stApp {{
    background: {CREAM};
    color: {TEXT};
    font-family: 'DM Sans', sans-serif;
}}

.block-container {{
    max-width: 900px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}}

h1, h2, h3 {{
    color: {DARK_GREEN};
}}

h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.65rem, 5vw, 2.3rem) !important;
}}

h2, h3 {{
    letter-spacing: -0.3px;
}}

.brand {{
    background: linear-gradient(135deg, #E6EEE6, #F9F8F3);
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 23px 20px;
    margin-bottom: 20px;
}}

.brand-kicker {{
    color: {GREEN};
    font-size: 0.72rem;
    letter-spacing: 2px;
    font-weight: 700;
}}

.brand-title {{
    color: {DARK_GREEN};
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.55rem, 5vw, 2.1rem);
    margin: 8px 0;
}}

.brand-subtitle {{
    color: {MUTED};
    font-size: 0.92rem;
    line-height: 1.6;
}}

.section-card {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 15px;
    padding: 16px;
    margin: 10px 0;
}}

.section-kicker {{
    color: {GREEN};
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.2px;
}}

div[data-testid="stForm"] {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 16px;
}}

.stButton > button,
.stDownloadButton > button,
div[data-testid="stFormSubmitButton"] button {{
    min-height: 46px;
    border-radius: 11px;
    font-weight: 600;
    width: 100%;
}}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"] {{
    background: {GREEN};
    border-color: {GREEN};
    color: white;
}}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {{
    border-radius: 9px;
}}

div[data-testid="stFileUploader"] {{
    background: white;
    border: 1px dashed {BORDER};
    border-radius: 12px;
    padding: 10px;
}}

div[data-testid="stAlert"] {{
    border-radius: 12px;
}}

.footer {{
    color: {MUTED};
    text-align: center;
    font-size: 0.78rem;
    padding: 20px 0 5px;
}}

@media (max-width: 600px) {{
    .block-container {{
        padding-top: 0.7rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }}
    .brand {{
        padding: 18px 15px;
    }}
    div[data-testid="stForm"] {{
        padding: 12px;
    }}
}}
</style>
""", unsafe_allow_html=True)


# =========================================================
# PDF YAZI TİPİ
# =========================================================

def register_font():
    font_paths = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ),
    ]

    for regular, bold in font_paths:
        if os.path.exists(regular) and os.path.exists(bold):
            try:
                pdfmetrics.registerFont(TTFont("ClinicFont", regular))
                pdfmetrics.registerFont(TTFont("ClinicFontBold", bold))
                return "ClinicFont", "ClinicFontBold"
            except Exception:
                pass

    return "Helvetica", "Helvetica-Bold"


def safe(value):
    return escape(str(value or "")).replace("\n", "<br/>")


# =========================================================
# PDF OLUŞTURMA
# =========================================================

def create_pdf(data, logo_bytes=None):
    regular, bold = register_font()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=14 * mm,
        bottomMargin=15 * mm,
        title=f"Diyet Programı - {data['name']}",
        author=data["dietitian"],
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="BrandTitle",
        fontName=bold,
        fontSize=18,
        leading=23,
        textColor=colors.HexColor(DARK_GREEN),
    ))
    styles.add(ParagraphStyle(
        name="MutedClinic",
        fontName=regular,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor(MUTED),
    ))
    styles.add(ParagraphStyle(
        name="SectionClinic",
        fontName=bold,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor(DARK_GREEN),
        spaceBefore=5,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="BodyClinic",
        fontName=regular,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor(TEXT),
        wordWrap="CJK",
    ))
    styles.add(ParagraphStyle(
        name="MealClinic",
        fontName=bold,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor(DARK_GREEN),
    ))
    styles.add(ParagraphStyle(
        name="TimeClinic",
        fontName=bold,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor(GREEN),
    ))
    styles.add(ParagraphStyle(
        name="FooterClinic",
        fontName=regular,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor(MUTED),
        alignment=TA_CENTER,
    ))

    story = []

    # Logo ve başlık
    brand_content = [
        Paragraph("DİYETİSYEN", styles["MutedClinic"]),
        Spacer(1, 2),
        Paragraph(safe(data["dietitian"]), styles["BrandTitle"]),
        Spacer(1, 3),
        Paragraph("KİŞİYE ÖZEL BESLENME PROGRAMI",
                  styles["MutedClinic"]),
    ]

    if logo_bytes:
        try:
            logo = PDFImage(
                io.BytesIO(logo_bytes),
                width=24 * mm,
                height=24 * mm,
                kind="proportional",
            )
            header = Table(
                [[logo, brand_content]],
                colWidths=[30 * mm, 135 * mm],
            )
        except Exception:
            header = Table([[brand_content]], colWidths=[165 * mm])
    else:
        header = Table([[brand_content]], colWidths=[165 * mm])

    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.extend([
        header,
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=colors.HexColor(GREEN),
            spaceAfter=10,
        ),
        Paragraph("DANIŞAN BİLGİLERİ", styles["SectionClinic"]),
    ])

    # Boy bilgisi kaldırıldı.
    client_rows = [
        [
            Paragraph("<b>Danışan</b>", styles["BodyClinic"]),
            Paragraph(safe(data["name"]), styles["BodyClinic"]),
        ],
        [
            Paragraph("<b>Program tarihi</b>", styles["BodyClinic"]),
            Paragraph(safe(data["program_date"]), styles["BodyClinic"]),
        ],
        [
            Paragraph("<b>Yaş</b>", styles["BodyClinic"]),
            Paragraph(safe(data["age"] or "Belirtilmedi"), styles["BodyClinic"]),
        ],
        [
            Paragraph("<b>Kilo</b>", styles["BodyClinic"]),
            Paragraph(safe(data["weight"] or "Belirtilmedi"), styles["BodyClinic"]),
        ],
        [
            Paragraph("<b>Hedef</b>", styles["BodyClinic"]),
            Paragraph(safe(data["goal"]), styles["BodyClinic"]),
        ],
    ]

    client_table = Table(client_rows, colWidths=[36 * mm, 129 * mm])
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(LIGHT_GREEN)),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(BORDER)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.extend([
        client_table,
        Spacer(1, 5 * mm),
        Paragraph("GÜNLÜK BESLENME PLANI", styles["SectionClinic"]),
    ])

    # Öğün adı + saat + içerik
    for meal in data["meals"]:
        description = meal["description"].strip()
        if not description:
            description = "Bu öğün için açıklama girilmemiştir."

        meal_table = Table(
            [[
                Paragraph(safe(meal["title"]), styles["MealClinic"]),
                Paragraph(safe(meal["time"]), styles["TimeClinic"]),
                Paragraph(safe(description), styles["BodyClinic"]),
            ]],
            colWidths=[34 * mm, 22 * mm, 109 * mm],
        )

        meal_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(LIGHT_GREEN)),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F4F7F3")),
            ("BACKGROUND", (2, 0), (2, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER)),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(BORDER)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        story.extend([KeepTogether([meal_table, Spacer(1, 2 * mm)])])

    if data["notes"].strip():
        story.extend([
            Spacer(1, 2 * mm),
            Paragraph("DİYETİSYEN NOTLARI", styles["SectionClinic"]),
        ])

        notes_table = Table(
            [[Paragraph(safe(data["notes"]), styles["BodyClinic"])]],
            colWidths=[165 * mm],
        )
        notes_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F8F4")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER)),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(notes_table)

    contact = "  •  ".join(
        value.strip()
        for value in [data["phone"], data["email"], data["website"]]
        if value.strip()
    )

    story.extend([
        Spacer(1, 6 * mm),
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor(BORDER),
            spaceAfter=6,
        ),
    ])

    if contact:
        story.extend([
            Paragraph(safe(contact), styles["FooterClinic"]),
            Spacer(1, 3 * mm),
        ])

    story.append(Paragraph(
        "Bu program, diyetisyen değerlendirmesi doğrultusunda uygulanmalıdır.",
        styles["FooterClinic"],
    ))

    doc.build(story)
    return buffer.getvalue()


# =========================================================
# TEK EKRANLI MOBİL UYUMLU ARAYÜZ
# =========================================================

st.markdown("""
<div class="brand">
    <div class="brand-kicker">BESLENME & YAŞAM</div>
    <div class="brand-title">Diyetisyen Sevgi Akbulut</div>
    <div class="brand-subtitle">
        Kişiye özel beslenme programını hazırla ve PDF olarak indir.
        Tüm işlemler tek ekranda.
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("Klinik bilgileri ve logo", expanded=False):
    dietitian = st.text_input(
        "Diyetisyen adı",
        value="Diyetisyen Sevgi Akbulut",
    )
    phone = st.text_input("Telefon", placeholder="Telefon numarası")
    email = st.text_input("E-posta", placeholder="E-posta adresi")
    website = st.text_input(
        "Web sitesi / sosyal medya",
        placeholder="Örn. Instagram hesabı",
    )
    logo_file = st.file_uploader(
        "Logo yükle (isteğe bağlı)",
        type=["png", "jpg", "jpeg"],
    )

logo_bytes = logo_file.getvalue() if logo_file else None

st.markdown("### 1. Danışan bilgileri")

with st.container(border=True):
    name = st.text_input(
        "Ad soyad *",
        placeholder="Danışanın adı ve soyadı",
    )

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Yaş", min_value=0, max_value=120, value=30)
    with col2:
        weight = st.number_input(
            "Kilo (kg)",
            min_value=0.0,
            max_value=500.0,
            value=0.0,
            step=0.1,
        )

    program_date = st.date_input("Program tarihi", value=date.today())

    goal = st.selectbox(
        "Program hedefi",
        [
            "Kişiye özel beslenme",
            "Kilo yönetimi",
            "Sağlıklı beslenme",
            "Sporcu beslenmesi",
            "Diğer",
        ],
    )

st.markdown("### 2. Günlük öğün programı")
st.caption("Her öğün için saati seç ve besinleri, miktarları ve açıklamaları gir.")

meal_names = [
    "Kahvaltı",
    "Ara Öğün 1",
    "Öğle Yemeği",
    "Ara Öğün 2",
    "Akşam Yemeği",
    "Gece Öğünü",
]

time_options = [
    f"{hour:02d}:{minute:02d}"
    for hour in range(5, 24)
    for minute in (0, 15, 30, 45)
]

meals = []

for i, meal_name in enumerate(meal_names):
    with st.container(border=True):
        st.markdown(f"**{i + 1:02d} · {meal_name}**")

        default_times = ["08:00", "10:30", "13:00", "16:00", "19:00", "21:30"]
        selected_time = st.selectbox(
            f"{meal_name} saati",
            options=time_options,
            index=time_options.index(default_times[i]),
            key=f"time_{i}",
        )

        description = st.text_area(
            f"{meal_name} içeriği",
            placeholder="Örn. besin adı, miktarı ve gerekli açıklamalar...",
            height=95,
            key=f"description_{i}",
        )

        meals.append({
            "title": meal_name,
            "time": selected_time,
            "description": description,
        })

st.markdown("### 3. Diyetisyen notları")

notes = st.text_area(
    "Danışana özel notlar",
    placeholder="Takip notları, hatırlatmalar veya ek açıklamalar...",
    height=100,
)

st.markdown("### 4. PDF oluştur ve indir")

st.caption(
    "PDF'de danışan bilgileri, öğün saatleri, öğün içerikleri, "
    "diyetisyen notları ve klinik iletişim bilgileri yer alır."
)

if st.button("PDF OLUŞTUR", type="primary", use_container_width=True):
    if not name.strip():
        st.error("PDF oluşturmadan önce danışanın adını ve soyadını gir.")
    else:
        data = {
            "name": name.strip(),
            "age": str(age) if age else "",
            "weight": f"{weight:g} kg" if weight else "",
            "program_date": program_date.strftime("%d.%m.%Y"),
            "goal": goal,
            "dietitian": dietitian.strip() or "Diyetisyen Sevgi Akbulut",
            "phone": phone,
            "email": email,
            "website": website,
            "notes": notes,
            "meals": meals,
        }

        try:
            st.session_state["pdf_output"] = create_pdf(data, logo_bytes)

            safe_filename = "".join(
                char for char in name
                if char.isalnum() or char in (" ", "-", "_")
            ).strip().replace(" ", "_")

            st.session_state["pdf_filename"] = (
                f"Diyet_Programi_{safe_filename or 'Danisan'}.pdf"
            )
            st.success("PDF hazır. Aşağıdaki düğmeyle bilgisayarına indirebilirsin.")
        except Exception as exc:
            st.error(f"PDF oluşturulurken hata oluştu: {exc}")

if st.session_state.get("pdf_output"):
    st.download_button(
        "⬇ PDF'Yİ BİLGİSAYARA İNDİR",
        data=st.session_state["pdf_output"],
        file_name=st.session_state.get(
            "pdf_filename", "Diyet_Programi.pdf"
        ),
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

st.markdown("""
<div class="footer">
    Diyetisyen Sevgi Akbulut · Beslenme ve danışan programları
</div>
""", unsafe_allow_html=True)
