
import io
import os
from datetime import date
from xml.sax.saxutils import escape

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as PDFImage, HRFlowable, KeepTogether
)

# ---------------------------------------------------------
# SAYFA VE TEMA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Diyetisyen Sevgi Akbulut",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
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

:root {{
    --green: {GREEN};
    --dark-green: {DARK_GREEN};
    --cream: {CREAM};
    --text: {TEXT};
}}
html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}}
.stApp {{
    background: var(--cream);
}}
[data-testid="stSidebar"] {{
    background: #FFFFFF;
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] h1 {{
    font-family: 'Playfair Display', serif;
    color: {DARK_GREEN};
}}
h1, h2, h3 {{
    color: {DARK_GREEN};
    letter-spacing: -0.4px;
}}
h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem !important;
}}
div[data-testid="stMetric"] {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    padding: 18px 20px;
    border-radius: 16px;
}}
.stButton > button, .stDownloadButton > button {{
    border-radius: 10px;
    min-height: 44px;
    font-weight: 600;
}}
.stButton > button[kind="primary"] {{
    background: {GREEN};
    border: 1px solid {GREEN};
    color: white;
}}
.stButton > button[kind="primary"]:hover {{
    background: {DARK_GREEN};
    border-color: {DARK_GREEN};
}}
input, textarea {{
    border-radius: 9px !important;
}}
div[data-testid="stForm"] {{
    background: white;
    border: 1px solid {BORDER};
    padding: 22px;
    border-radius: 16px;
}}
.brand-caption {{
    color: {MUTED};
    font-size: 0.83rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}
.hero {{
    background: linear-gradient(120deg, #E7EEE7 0%, #F7F6F1 100%);
    border: 1px solid #DFE7DF;
    border-radius: 20px;
    padding: 28px 30px;
    margin-bottom: 24px;
}}
.hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: {DARK_GREEN};
    margin-bottom: 8px;
}}
.hero-sub {{
    color: #66756A;
    font-size: 0.98rem;
}}
.section-label {{
    color: {GREEN};
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}}
.small-note {{
    font-size: 0.86rem;
    color: {MUTED};
}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# PDF YARDIMCILARI
# ---------------------------------------------------------

def register_turkish_font():
    """Uygun bir Unicode yazı tipi varsa PDF için kaydeder."""
    candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ),
        (
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
        ),
    ]

    for regular, bold in candidates:
        if os.path.exists(regular) and os.path.exists(bold):
            try:
                pdfmetrics.registerFont(TTFont("ClinicFont", regular))
                pdfmetrics.registerFont(TTFont("ClinicFontBold", bold))
                return "ClinicFont", "ClinicFontBold"
            except Exception:
                continue

    return "Helvetica", "Helvetica-Bold"


def safe_text(value):
    """Kullanıcı girdilerini ReportLab paragrafına güvenli aktarır."""
    return escape(str(value or "")).replace("\n", "<br/>")


def make_pdf(data, logo_bytes=None):
    regular_font, bold_font = register_turkish_font()
    output = io.BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=17 * mm,
        title=f"Diyet Programı - {data['name']}",
        author=data["dietitian"],
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Brand",
        fontName=bold_font,
        fontSize=19,
        leading=24,
        textColor=colors.HexColor(DARK_GREEN),
        alignment=TA_LEFT,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="SubBrand",
        fontName=regular_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(MUTED),
    ))
    styles.add(ParagraphStyle(
        name="Section",
        fontName=bold_font,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor(DARK_GREEN),
        spaceBefore=8,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="BodyClinic",
        fontName=regular_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(TEXT),
    ))
    styles.add(ParagraphStyle(
        name="MealTitle",
        fontName=bold_font,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor(DARK_GREEN),
    ))
    styles.add(ParagraphStyle(
        name="Foot",
        fontName=regular_font,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(MUTED),
        alignment=TA_CENTER,
    ))

    story = []

    # Logo ve üst başlık
    brand_cell = [
        Paragraph("DİYETİSYEN", styles["SubBrand"]),
        Paragraph(safe_text(data["dietitian"]), styles["Brand"]),
        Paragraph("KİŞİYE ÖZEL BESLENME PROGRAMI", styles["SubBrand"]),
    ]

    if logo_bytes:
        try:
            logo = PDFImage(io.BytesIO(logo_bytes), width=25 * mm, height=25 * mm)
            logo.hAlign = "LEFT"
            header = Table([[logo, brand_cell]], colWidths=[31 * mm, 135 * mm])
        except Exception:
            header = Table([[brand_cell]], colWidths=[166 * mm])
    else:
        header = Table([[brand_cell]], colWidths=[166 * mm])

    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.extend([header, HRFlowable(
        width="100%", thickness=1.2,
        color=colors.HexColor(GREEN), spaceAfter=12
    )])

    # Danışan kartı
    story.append(Paragraph("DANIŞAN BİLGİLERİ", styles["Section"]))

    client_rows = [
        [
            Paragraph("<b>Danışan</b>", styles["BodyClinic"]),
            Paragraph(safe_text(data["name"]), styles["BodyClinic"]),
            Paragraph("<b>Program tarihi</b>", styles["BodyClinic"]),
            Paragraph(safe_text(data["program_date"]), styles["BodyClinic"]),
        ],
        [
            Paragraph("<b>Yaş</b>", styles["BodyClinic"]),
            Paragraph(safe_text(data["age"] or "Belirtilmedi"), styles["BodyClinic"]),
            Paragraph("<b>Hedef</b>", styles["BodyClinic"]),
            Paragraph(safe_text(data["goal"] or "Belirtilmedi"), styles["BodyClinic"]),
        ],
        [
            Paragraph("<b>Boy</b>", styles["BodyClinic"]),
            Paragraph(safe_text(data["height"] or "Belirtilmedi"), styles["BodyClinic"]),
            Paragraph("<b>Kilo</b>", styles["BodyClinic"]),
            Paragraph(safe_text(data["weight"] or "Belirtilmedi"), styles["BodyClinic"]),
        ],
    ]

    client_table = Table(
        client_rows,
        colWidths=[24 * mm, 58 * mm, 27 * mm, 57 * mm],
    )
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F7F3")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(BORDER)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([client_table, Spacer(1, 8 * mm)])

    # Altı sabit öğün
    story.append(Paragraph("GÜNLÜK BESLENME PLANI", styles["Section"]))

    for meal in data["meals"]:
        description = safe_text(meal["description"]).strip()
        if not description:
            description = "Bu öğün için açıklama girilmemiştir."

        meal_table = Table(
            [[
                Paragraph(safe_text(meal["title"]), styles["MealTitle"]),
                Paragraph(description, styles["BodyClinic"]),
            ]],
            colWidths=[39 * mm, 127 * mm],
        )
        meal_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(LIGHT_GREEN)),
            ("BACKGROUND", (1, 0), (1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER)),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(BORDER)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.extend([KeepTogether([meal_table, Spacer(1, 2 * mm)])])

    # Notlar
    if data["notes"].strip():
        story.append(Paragraph("DİYETİSYEN NOTLARI", styles["Section"]))
        note_table = Table(
            [[Paragraph(safe_text(data["notes"]), styles["BodyClinic"])]],
            colWidths=[166 * mm],
        )
        note_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F8F4")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER)),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.extend([note_table, Spacer(1, 5 * mm)])

    # İletişim ve dipnot
    contact = "  •  ".join(
        x for x in [
            data["phone"].strip(),
            data["email"].strip(),
            data["website"].strip(),
        ] if x
    )
    if contact:
        story.append(Paragraph(safe_text(contact), styles["Foot"]))
        story.append(Spacer(1, 3 * mm))

    story.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor(BORDER), spaceBefore=2, spaceAfter=5
    ))
    story.append(Paragraph(
        "Bu program danışana özel olarak hazırlanmıştır. "
        "Uygulama ve takip, diyetisyen değerlendirmesi doğrultusunda yürütülmelidir.",
        styles["Foot"],
    ))

    doc.build(story)
    return output.getvalue()


# ---------------------------------------------------------
# OTURUM DURUMU
# ---------------------------------------------------------

MEAL_NAMES = [
    "Kahvaltı",
    "Ara Öğün 1",
    "Öğle Yemeği",
    "Ara Öğün 2",
    "Akşam Yemeği",
    "Gece Öğünü",
]

if "generated_pdf" not in st.session_state:
    st.session_state.generated_pdf = None

if "generated_filename" not in st.session_state:
    st.session_state.generated_filename = "diyet_programi.pdf"


# ---------------------------------------------------------
# SOL MENÜ
# ---------------------------------------------------------

with st.sidebar:
    st.markdown(
        f"<div style='color:{GREEN};font-size:12px;letter-spacing:2px'>"
        "BESLENME & YAŞAM</div>",
        unsafe_allow_html=True,
    )
    st.markdown("# Sevgi Akbulut")
    st.caption("Diyetisyen Yönetim Paneli")
    st.divider()

    page = st.radio(
        "MENÜ",
        ["Ana Sayfa", "Diyet Programı", "PDF Oluştur"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Klinik bilgileri**")
    dietitian = st.text_input(
        "Diyetisyen adı",
        value="Diyetisyen Sevgi Akbulut",
        key="dietitian",
    )
    phone = st.text_input("Telefon", placeholder="Telefon numarası")
    email = st.text_input("E-posta", placeholder="E-posta adresi")
    website = st.text_input("Web sitesi", placeholder="Web sitesi veya sosyal medya")

    logo_file = st.file_uploader(
        "Klinik logosu (isteğe bağlı)",
        type=["png", "jpg", "jpeg"],
        help="Yüklediğin logo PDF başlığında kullanılacaktır.",
    )
    logo_bytes = logo_file.getvalue() if logo_file else None

    st.markdown(
        "<div class='small-note'>Veri tabanı kullanılmaz. "
        "PDF dosyalarını bilgisayarına indirerek saklayabilirsin.</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# SAYFA: ANA SAYFA
# ---------------------------------------------------------

if page == "Ana Sayfa":
    st.markdown("<div class='brand-caption'>KLİNİK ÇALIŞMA ALANI</div>",
                unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">Beslenme planlarını özenle hazırla.</div>
            <div class="hero-sub">
                Diyetisyen Sevgi Akbulut için sade, düzenli ve profesyonel
                program hazırlama alanı.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Öğün düzeni", "6 öğün", "Sabit şablon")
    c2.metric("Çıktı formatı", "PDF", "Bilgisayara indir")
    c3.metric("Veri tabanı", "Yok", "Yerel arşiv")

    st.markdown("### Çalışma alanı")
    st.write(
        "Danışan bilgilerini gir, günlük öğün açıklamalarını düzenle "
        "ve kişiye özel PDF programını oluştur."
    )

    left, right = st.columns(2)
    with left:
        st.markdown("#### 🌿 Diyet programı")
        st.write("Danışan bilgilerini ve altı öğünün içeriğini hazırla.")
        if st.button("Yeni program hazırla", type="primary", use_container_width=True):
            st.session_state.generated_pdf = None
            st.session_state["requested_page"] = "Diyet Programı"
            st.rerun()

    with right:
        st.markdown("#### 📄 PDF çıktısı")
        st.write("Hazırladığın programı düzenli bir PDF dosyasına dönüştür.")
        if st.button("PDF alanına git", use_container_width=True):
            st.session_state["requested_page"] = "PDF Oluştur"
            st.rerun()

    st.info(
        "Önemli: Bu sürümde danışan listesi veya geçmiş program arşivi yoktur. "
        "İndirdiğin PDF dosyalarını kendi bilgisayarında güvenli bir klasörde sakla."
    )


# ---------------------------------------------------------
# SAYFA: DİYET PROGRAMI
# ---------------------------------------------------------

elif page == "Diyet Programı":
    st.markdown("<div class='brand-caption'>PROGRAM HAZIRLAMA</div>",
                unsafe_allow_html=True)
    st.title("Diyet programı")
    st.write("Danışan bilgilerini doldur ve her öğün için açıklama ekle.")

    with st.form("diet_form"):
        st.markdown("### 01 · Danışan bilgileri")

        name = st.text_input("Ad soyad *", placeholder="Danışanın adı ve soyadı")
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Yaş", min_value=0, max_value=120, value=30)
        with col2:
            height = st.number_input("Boy (cm)", min_value=0, max_value=250, value=0)
        with col3:
            weight = st.number_input("Kilo (kg)", min_value=0.0, max_value=500.0,
                                     value=0.0, step=0.1)

        col4, col5 = st.columns(2)
        with col4:
            program_date = st.date_input("Program tarihi", value=date.today())
        with col5:
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

        st.divider()
        st.markdown("### 02 · Günlük öğünler")
        st.caption("Her alanı danışana özel içerikle doldur.")

        meal_descriptions = {}
        meal_cols = st.columns(2)

        for i, meal_name in enumerate(MEAL_NAMES):
            with meal_cols[i % 2]:
                st.markdown(f"**{i + 1:02d} · {meal_name}**")
                meal_descriptions[meal_name] = st.text_area(
                    f"{meal_name} içeriği",
                    key=f"meal_{i}",
                    placeholder="Besinleri, miktarları ve gerekli açıklamaları yaz...",
                    height=110,
                    label_visibility="collapsed",
                )

        st.divider()
        st.markdown("### 03 · Diyetisyen notları")
        notes = st.text_area(
            "Notlar",
            placeholder="Takip notları, özel hatırlatmalar veya danışana iletilecek açıklamalar...",
            height=110,
        )

        submitted = st.form_submit_button(
            "Programı kaydet ve PDF alanına geç",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not name.strip():
            st.error("Lütfen danışanın adını ve soyadını gir.")
        else:
            st.session_state.diet_data = {
                "name": name.strip(),
                "age": str(age) if age else "",
                "height": f"{height} cm" if height else "",
                "weight": f"{weight:g} kg" if weight else "",
                "goal": goal,
                "program_date": program_date.strftime("%d.%m.%Y"),
                "dietitian": dietitian.strip() or "Diyetisyen Sevgi Akbulut",
                "phone": phone,
                "email": email,
                "website": website,
                "notes": notes,
                "meals": [
                    {
                        "title": meal_name,
                        "description": meal_descriptions[meal_name],
                    }
                    for meal_name in MEAL_NAMES
                ],
            }
            st.session_state.generated_pdf = None
            st.success("Program bilgileri hazırlandı. PDF oluşturma sayfasına geçebilirsin.")
            st.session_state["requested_page"] = "PDF Oluştur"


# ---------------------------------------------------------
# SAYFA: PDF OLUŞTUR
# ---------------------------------------------------------

elif page == "PDF Oluştur":
    st.markdown("<div class='brand-caption'>DIŞA AKTARMA</div>",
                unsafe_allow_html=True)
    st.title("PDF oluştur")
    st.write("Programı kontrol et, PDF'yi üret ve bilgisayarına indir.")

    data = st.session_state.get("diet_data")

    if not data:
        st.warning(
            "Henüz bir program hazırlanmadı. Önce Diyet Programı sayfasından "
            "danışan bilgilerini ve öğünleri doldur."
        )
        if st.button("Diyet programına git", type="primary"):
            st.session_state["requested_page"] = "Diyet Programı"
            st.rerun()
    else:
        a, b = st.columns(2)
        with a:
            st.markdown("#### Danışan")
            st.write(data["name"])
            st.caption(f"Program tarihi: {data['program_date']}")
        with b:
            st.markdown("#### Öğün planı")
            st.write("6 sabit öğün")
            st.caption(f"Diyetisyen: {data['dietitian']}")

        st.divider()

        with st.expander("PDF öncesi öğünleri kontrol et", expanded=True):
            for meal in data["meals"]:
                st.markdown(f"**{meal['title']}**")
                st.write(meal["description"] or "Henüz açıklama girilmedi.")
                st.divider()

        filename_base = "".join(
            ch for ch in data["name"]
            if ch.isalnum() or ch in (" ", "-", "_")
        ).strip().replace(" ", "_")
        filename = f"Diyet_Programi_{filename_base or 'Danisan'}.pdf"

        if st.button("✨ PDF oluştur", type="primary", use_container_width=True):
            try:
                st.session_state.generated_pdf = make_pdf(data, logo_bytes)
                st.session_state.generated_filename = filename
                st.success("PDF başarıyla oluşturuldu.")
            except Exception as exc:
                st.error(f"PDF oluşturulamadı: {exc}")

        if st.session_state.generated_pdf:
            st.download_button(
                label="⬇ PDF'yi bilgisayara indir",
                data=st.session_state.generated_pdf,
                file_name=st.session_state.generated_filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

        st.caption(
            "İndirme işlemi tarayıcının indirme klasörüne yapılır. "
            "PDF dosyasını açıp Türkçe karakterleri ve içerikleri kontrol et."
        )

st.divider()
st.markdown(
    f"<div style='text-align:center;color:{MUTED};font-size:12px'>"
    "Diyetisyen Sevgi Akbulut · Beslenme ve danışan programları"
    "</div>",
    unsafe_allow_html=True,
)
