import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import utils

# =========================================================
# 1. إعدادات الصفحة الأساسية (يجب أن تكون أول سطر)
# =========================================================
st.set_page_config(
    page_title="EGX AI – Stock Assistant",
    layout="wide"
)

# رابط قاعدة بيانات المستخدمين (Google Sheets)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3C5XF45Cl-a8w_msij3UsPCBiyP6XRQ6GbhN1-01wT3lq-Bw2CL5bYc9ZBQTcHKQnk_g6KsqPKYaZ/pub?output=csv"

# =========================================================
# 2. نظام تسجيل الدخول وتنسيق الصور
# =========================================================
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        # تنسيق البانر واللوجو بالقياسات المطلوبة (3سم و 2سم تقريباً)
        st.markdown(
            """
            <style>
            .main-banner {
                width: 100%;
                height: 115px; /* ارتفاع 3 سم تقريباً */
                object-fit: cover;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .logo-container {
                display: flex;
                justify-content: center;
                margin-bottom: 10px;
            }
            .logo-img {
                width: 75px; /* عرض 2 سم تقريباً */
                height: 75px; /* ارتفاع 2 سم تقريباً */
                object-fit: contain;
            }
            </style>
            """, unsafe_allow_html=True
        )

        # عرض البانر
        try:
            st.image("pics/banner.jpg", use_container_width=True)
        except: pass

        # عرض اللوجو تحت البانر في المنتصف
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            try:
                st.image("pics/logo.jpeg", width=75) # حجم 2 سم
            except: pass
            st.markdown("<h3 style='text-align: center;'>🔐 تسجيل الدخول</h3>", unsafe_allow_html=True)

        # نموذج تسجيل الدخول
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            submitted = st.form_submit_button("دخول للنظام", use_container_width=True)
            
            if submitted:
                try:
                    df_u = pd.read_csv(SHEET_URL)
                    df_u['username'] = df_u['username'].astype(str).str.strip()
                    df_u['password'] = df_u['password'].astype(str).str.strip()
                    user_row = df_u[df_u['username'] == str(u).strip()]
                    
                    if not user_row.empty and str(user_row.iloc[0]['password']) == str(p).strip():
                        st.session_state['logged_in'] = True
                        st.session_state['role'] = user_row.iloc[0].get('role', 'User')
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                except Exception as e:
                    st.error(f"⚠️ خطأ في الاتصال: تأكد من وجود مكتبة openpyxl")
        
        st.stop() # يمنع ظهور باقي البرنامج حتى يسجل الدخول
        return False
    return True

# استدعاء الحماية فوراً
check_login()

# =========================
# 3. مسارات رئيسية وتحميل البيانات
# =========================
BASE_DIR = Path(__file__).resolve().parent
INTRADAY_DIR = BASE_DIR / "intraday"
TRANSACTION_DIR = BASE_DIR / "transaction"

def get_latest_file(folder: Path, pattern: str):
    files = [f for f in folder.glob(pattern) if not f.name.startswith(("~$", "-$"))]
    if not files: return None
    files = sorted(files, key=lambda f: f.stat().st_mtime)
    return files[-1]

@st.cache_data(show_spinner=False)
def load_daily_data():
    intraday_path = get_latest_file(INTRADAY_DIR, "*.xlsx")
    tx_path = get_latest_file(TRANSACTION_DIR, "*.csv")
    df_intraday = utils.load_intraday(intraday_path) if intraday_path else None
    df_tx = utils.load_transactions(tx_path) if tx_path else None
    signals = None
    if intraday_path and tx_path:
        signals = utils.build_signals_for_day(intraday_path, tx_path)
        signals = utils.apply_ai_score(signals)
    return df_intraday, df_tx, signals, intraday_path, tx_path

df_intraday, df_tx, signals, intraday_path, tx_path = load_daily_data()

# =========================================================
# 4. القائمة الجانبية (Sidebar)
# =========================================================
st.sidebar.title("EGX AI Navigation")
page = st.sidebar.radio(
    "إختر صفحة",
    ["📊 Market Overview", "📈 Technical View", "📉 S/R Breakouts", "🤖 AI Recommendations", "📌 Group Picks Ranking", "🧠 AI & News Analytics"]
)

# عرض بيانات المطور في السايدبار
st.sidebar.markdown("---")
try:
    st.sidebar.image("pics/photo.jpg", use_container_width=True)
except: pass

st.sidebar.markdown(f"""
<div style="text-align: right; direction: rtl; border: 1px solid #444; padding: 10px; border-radius: 10px; background-color: #1e1e1e;">
    <p style="color: #ff4b4b; font-weight: bold; font-size: 16px; margin:0;">Nader Al-Saed Shalaby</p>
    <p style="font-size: 12px; color: #ccc; margin:0;">Investment Manager (EGX)</p>
    <p style="font-size: 12px; color: #4CAF50; margin:0;">📞 01016675600</p>
</div>
""", unsafe_allow_html=True)

# =========================
# 4. مسارات البيانات وتحميلها
# =========================
BASE_DIR = Path(__file__).resolve().parent
INTRADAY_DIR = BASE_DIR / "intraday"
TRANSACTION_DIR = BASE_DIR / "transaction"

def get_latest_file(folder: Path, pattern: str):
    files = [f for f in folder.glob(pattern) if not f.name.startswith(("~$", "-$"))]
    if not files: return None
    files = sorted(files, key=lambda f: f.stat().st_mtime)
    return files[-1]

@st.cache_data(show_spinner=False)
def load_daily_data():
    intraday_path = get_latest_file(INTRADAY_DIR, "*.xlsx")
    tx_path = get_latest_file(TRANSACTION_DIR, "*.csv")
    df_intraday = utils.load_intraday(intraday_path) if intraday_path else None
    df_tx = utils.load_transactions(tx_path) if tx_path else None
    signals = None
    if intraday_path and tx_path:
        signals = utils.build_signals_for_day(intraday_path, tx_path)
        signals = utils.apply_ai_score(signals)
    return df_intraday, df_tx, signals, intraday_path, tx_path

df_intraday, df_tx, signals, intraday_path, tx_path = load_daily_data()

# عرض الحالة في الـ sidebar تحت بياناتك
if intraday_path: st.sidebar.success(f"Intraday: {intraday_path.name}")
else: st.sidebar.error("لا يوجد ملف Intraday متاح.")

if tx_path: st.sidebar.success(f"Transactions: {tx_path.name}")
else: st.sidebar.error("لا يوجد ملف Transactions متاح.")

# =========================================================
# 📊 صفحة Market Overview
# =========================================================
if page == "📊 Market Overview":
    st.title("📊 Market Overview – نظرة عامة على السوق")

    if df_intraday is None or df_intraday.empty:
        st.warning("لا توجد بيانات Intraday متاحة.")
        st.stop()

    df = df_intraday.copy()

    # إزالة المؤشرات العامة (EGX30, EGX100.. إلخ) من عرض الأسهم
    df = df[~df["Symbol"].isin(utils.INDEX_SYMBOLS)]

    # نضمن وجود الأعمدة الأساسية
    for col in ["% Change", "Volume", "Turnover",
                "Cash in Turnover", "Cash Out Turnover"]:
        if col not in df.columns:
            df[col] = 0

    # أعلى 10 أسهم ربحاً / خسارة
    top_gainers = df.sort_values("% Change", ascending=False).head(10)
    top_losers = df.sort_values("% Change", ascending=True).head(10)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("أعلى 10 أسهم ربحاً")
        st.dataframe(
            top_gainers[["Symbol", "S. Description", "Last", "% Change", "Volume"]],
            use_container_width=True
        )
    with col2:
        st.subheader("أكثر 10 أسهم خسارة")
        st.dataframe(
            top_losers[["Symbol", "S. Description", "Last", "% Change", "Volume"]],
            use_container_width=True
        )

    st.subheader("رسم بيانى لأعلى الرابحين")
    chart_df = top_gainers.set_index("Symbol")["% Change"]
    st.bar_chart(chart_df)

    # أعلى حجم تداول / أعلى قيمة تداول / أقوى دخول وخروج سيولة
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.caption("أعلى حجم تداول")
        top_vol = df.sort_values("Volume", ascending=False).head(10)
        st.dataframe(
            top_vol[["Symbol", "S. Description", "Volume"]],
            use_container_width=True
        )

    with c2:
        st.caption("أعلى قيمة تداول")
        top_turn = df.sort_values("Turnover", ascending=False).head(10)
        st.dataframe(
            top_turn[["Symbol", "S. Description", "Turnover"]],
            use_container_width=True
        )

    with c3:
        st.caption("أقوى دخول سيولة (Cash in)")
        if "Cash in Turnover" in df.columns:
            top_in = df.sort_values("Cash in Turnover", ascending=False).head(10)
            st.dataframe(
                top_in[["Symbol", "S. Description", "Cash in Turnover"]],
                use_container_width=True
            )
        else:
            st.info("لا يوجد عمود Cash in Turnover فى ملف الجلسة.")

    with c4:
        st.caption("أقوى خروج سيولة (Cash Out)")
        if "Cash Out Turnover" in df.columns:
            top_out = df.sort_values("Cash Out Turnover", ascending=False).head(10)
            st.dataframe(
                top_out[["Symbol", "S. Description", "Cash Out Turnover"]],
                use_container_width=True
            )
        else:
            st.info("لا يوجد عمود Cash Out Turnover فى ملف الجلسة.")

    # نشاط القطاعات
    st.markdown("---")
    st.subheader("نشاط القطاعات (حسب حجم التداول)")
    if "Sector" in df.columns:
        sector_vol = df.groupby("Sector")["Volume"].sum().sort_values(ascending=False)
        st.bar_chart(sector_vol)
    else:
        st.info("ملف intraday لا يحتوى على عمود القطاع (Sector).")


# =========================================================
# 📈 صفحة Technical View
# =========================================================
elif page == "📈 Technical View":
    st.title("📈 Technical View – المؤشرات الفنية و الشارتات")

    if df_intraday is None or df_intraday.empty:
        st.warning("لا توجد بيانات لحظية (intraday) متاحة.")
        st.stop()

    if "Symbol" not in df_intraday.columns:
        st.error("ملف intraday لا يحتوى على عمود Symbol.")
        st.stop()

    # تجهيز قائمة الرموز
    df_intraday["Symbol"] = df_intraday["Symbol"].astype(str)
    symbols_all = sorted(df_intraday["Symbol"].dropna().unique())

    # خانة بحث
    search_text = st.text_input("اكتب رمز السهم أو جزء من الاسم:", "")

    if search_text.strip():
        mask = df_intraday["Symbol"].str.contains(search_text.strip(), case=False, na=False)
        if "S. Description" in df_intraday.columns:
            mask |= df_intraday["S. Description"].astype(str).str.contains(
                search_text.strip(), case=False, na=False
            )
        filtered_symbols = sorted(df_intraday.loc[mask, "Symbol"].unique())
        if not filtered_symbols:
            st.warning("لا يوجد أى سهم يطابق النص الذى أدخلته.")
            st.stop()
    else:
        filtered_symbols = symbols_all

    symbol = st.selectbox("اختر سهم للتحليل الفني من النتائج:", filtered_symbols)

    if not symbol:
        st.stop()

    st.subheader(f"ملخص المؤشرات الفنية للسهم: {symbol}")

    # -------- بيانات CASE (تاريخية) --------
    try:
        df_case = utils.load_case(symbol)
    except FileNotFoundError:
        df_case = None
        st.warning("لا يوجد ملف CASE لهذا السهم داخل مجلد CASE – سيتم الاعتماد على بيانات اليوم فقط.")
    except Exception as e:
        df_case = None
        st.error(f"خطأ أثناء قراءة بيانات CASE: {e}")

    # -------- صف السهم فى intraday --------
    row_intr = df_intraday[df_intraday["Symbol"] == symbol].copy()
    if row_intr.empty:
        st.error("لم يتم العثور على السهم فى ملف intraday.")
        st.stop()
    row_intr = row_intr.iloc[0]

    # أسعار اليوم / الإقفال السابق
    last_price = float(row_intr.get("Last", np.nan)) if not pd.isna(row_intr.get("Last", np.nan)) else np.nan
    prev_close = float(row_intr.get("Prev. Closed", np.nan)) if not pd.isna(row_intr.get("Prev. Closed", np.nan)) else np.nan

    # فى حالة عدم وجود آخر سعر / إقفال سابق نستعين بملف CASE
    if df_case is not None and (np.isnan(last_price) or np.isnan(prev_close)):
        df_case_sorted = df_case.sort_values("Date")
        if np.isnan(last_price) and "Closed" in df_case_sorted.columns:
            last_price = float(df_case_sorted["Closed"].iloc[-1])
        if np.isnan(prev_close) and "Prev. Closed" in df_case_sorted.columns:
            prev_close = float(df_case_sorted["Prev. Closed"].iloc[-1])

    # نسبة التغير اليومى من ملف الجلسة مباشرة
    change_pct = row_intr.get("% Change", np.nan)
    if not pd.isna(change_pct):
        change_pct = float(change_pct)

    # Pivot / R1 / R2 / S1 / S2 (لو مش موجودة نحسبها)
    row_intr_full = utils.add_pivot_levels(df_intraday[df_intraday["Symbol"] == symbol]).iloc[0]
    r1 = float(row_intr_full.get("Resistance 1 (R1)", np.nan)) if not pd.isna(row_intr_full.get("Resistance 1 (R1)", np.nan)) else np.nan
    r2 = float(row_intr_full.get("Resistance 2 (R2)", np.nan)) if not pd.isna(row_intr_full.get("Resistance 2 (R2)", np.nan)) else np.nan
    s1 = float(row_intr_full.get("Support 1 (S1)", np.nan)) if not pd.isna(row_intr_full.get("Support 1 (S1)", np.nan)) else np.nan
    s2 = float(row_intr_full.get("Support 2 (S2)", np.nan)) if not pd.isna(row_intr_full.get("Support 2 (S2)", np.nan)) else np.nan
    pivot = float(row_intr_full.get("Pivot Point", np.nan)) if not pd.isna(row_intr_full.get("Pivot Point", np.nan)) else np.nan

    # -------- المؤشرات من CASE (MA20/MA50/Vol20 + RSI) --------
    ma20 = ma50 = vol20 = None
    rsi_last = None

    if df_case is not None and not df_case.empty:
        try:
            tech_last = utils.compute_basic_technicals(df_case)
            ma20 = float(tech_last["MA20"].iloc[0]) if not pd.isna(tech_last["MA20"].iloc[0]) else None
            ma50 = float(tech_last["MA50"].iloc[0]) if not pd.isna(tech_last["MA50"].iloc[0]) else None
            vol20 = float(tech_last["Vol20"].iloc[0]) if not pd.isna(tech_last["Vol20"].iloc[0]) else None
        except Exception:
            pass

        # RSI 14 يوم
        try:
            close_series = None
            if "Closed" in df_case.columns:
                close_series = pd.to_numeric(df_case["Closed"], errors="coerce")
            elif "Close" in df_case.columns:
                close_series = pd.to_numeric(df_case["Close"], errors="coerce")

            if close_series is not None and len(close_series) > 14:
                delta = close_series.diff()
                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)
                avg_gain = gain.rolling(14).mean()
                avg_loss = loss.rolling(14).mean()
                rs = avg_gain / avg_loss.replace(0, np.nan)
                rsi = 100 - 100 / (1 + rs)
                rsi_last = float(rsi.iloc[-1])
        except Exception:
            rsi_last = None

    # -------- سلوك الجلسة من جدول الإشارات --------
    behavior_label = "غير متاح"
    behavior_expl = "لا توجد بيانات معاملات كافية لهذا السهم فى جلسة اليوم."
    buy_ratio_val = None

    if signals is not None and not signals.empty:
        row_sig = signals[signals["Symbol"].astype(str) == str(symbol)]
        if not row_sig.empty:
            row_sig = row_sig.iloc[0]
            behavior_label = row_sig.get("behavior", "غير متاح")
            buy_ratio_val = row_sig.get("buy_ratio", None)
            if behavior_label == "Accumulation":
                behavior_expl = "يوجد تجميع واضح على السهم (سيولة داخلة أعلى من الخارجة)."
            elif behavior_label == "Distribution":
                behavior_expl = "يوجد تصريف واضح على السهم (سيولة خارجة أعلى من الداخلة)."
            else:
                behavior_expl = "سلوك طبيعى بدون تجميع أو تصريف واضح."

    # -------- تحليل الاتجاه من MA20 / MA50 --------
    trend_label = "غير محدد"
    trend_expl = "لا يمكن تحديد الاتجاه لعدم توفر متوسطات كافية."
    if (ma20 is not None) and (ma50 is not None) and (last_price is not None):
        if last_price > ma20 > ma50:
            trend_label = "اتجاه صاعد"
            trend_expl = "السعر أعلى من MA20 و MA50، مما يدل على اتجاه صاعد مستقر."
        elif last_price < ma20 < ma50:
            trend_label = "اتجاه هابط"
            trend_expl = "السعر أسفل MA20 و MA50، مما يدل على ضغط بيعى واتجاه هابط."
        else:
            trend_label = "تذبذب / تجميع"
            trend_expl = "السعر بين المتوسطين، مما يشير إلى حركة عرضية أو تجميع."

    # -------- تفسير RSI --------
    rsi_label = "غير متاح"
    rsi_expl = "لم يتم حساب RSI لعدم كفاية البيانات."
    if rsi_last is not None:
        if rsi_last < 30:
            rsi_label = "تشبّع بيع (Oversold)"
            rsi_expl = "السهم فى منطقة تشبع بيع، قد يكون مناسباً للمراقبة لفرص الشراء التدريجى."
        elif rsi_last > 70:
            rsi_label = "تشبّع شراء (Overbought)"
            rsi_expl = "السهم فى منطقة تشبع شراء، يُفضّل الحذر من الشراء الجديد وتوقّع جنى أرباح."
        else:
            rsi_label = "منطقة حيادية"
            rsi_expl = "RSI فى المنطقة المتوسطة، لا يوجد تشبع واضح شراءً أو بيعًا."

    # -------- تذبذب السعر (Range) --------
    vol_label = "غير متاح"
    vol_expl = "لا توجد بيانات كافية لحساب التذبذب."
    vol20_str = None
    if vol20 is not None:
        vol20_str = f"{vol20:,.0f}"

    if "Range" in row_intr.index and not pd.isna(row_intr["Range"]):
        rng = float(row_intr["Range"])
        if rng < 1:
            vol_label = "تذبذب منخفض"
            vol_expl = "حركة السعر هادئة نسبيًا، مناسب أكثر للاستثمار الهادئ."
        elif rng < 3:
            vol_label = "تذبذب متوسط"
            vol_expl = "تذبذب طبيعى يمكن استغلاله للتداول قصير ومتوسط الأجل."
        else:
            vol_label = "تذبذب مرتفع"
            vol_expl = "السهم عالى التذبذب، مناسب للمضارب قصير الأجل مع وقف خسارة صارم."
    elif vol20 is not None:
        vol_label = "نشاط متوسط / عالى"
        vol_expl = "متوسط حجم التداول على 20 يوم يشير إلى وجود سيولة نشطة نسبيًا."

    # -------- جدولة المؤشرات الفنية الأساسية --------
    rows = []

    # 1) سعر الإغلاق والتغير
    price_row_expl = "السعر الحالى مقارنة بالجلسة السابقة."
    direction = "غير متاح"
    if change_pct is not None and not pd.isna(change_pct):
        if change_pct > 0:
            direction = "ارتفاع"
        elif change_pct < 0:
            direction = "انخفاض"
        else:
            direction = "بدون تغيير تقريبًا"
        price_row_expl = f"السهم يحقق {direction} اليوم بنسبة تقريبية {change_pct:.2f}%."

    rows.append({
        "المؤشر": "سعر الإغلاق والتغير اليومى",
        "القيمة": f"{last_price:.2f}" + (f" (تغير {change_pct:.2f}%)" if change_pct is not None and not pd.isna(change_pct) else ""),
        "حالة السهم": direction,
        "تفسير وتأثير على القرار": price_row_expl,
    })

    # 2) مستويات Pivot / دعم / مقاومة
    sr_val = []
    if not np.isnan(pivot):
        sr_val.append(f"Pivot ≈ {pivot:.2f}")
    if not np.isnan(s1):
        sr_val.append(f"S1 ≈ {s1:.2f}")
    if not np.isnan(s2):
        sr_val.append(f"S2 ≈ {s2:.2f}")
    if not np.isnan(r1):
        sr_val.append(f"R1 ≈ {r1:.2f}")
    if not np.isnan(r2):
        sr_val.append(f"R2 ≈ {r2:.2f}")
    sr_val_str = " / ".join(sr_val) if sr_val else "غير متاح"

    rows.append({
        "المؤشر": "مستويات الدعم والمقاومة لليوم",
        "القيمة": sr_val_str,
        "حالة السهم": "نطاق حركة سعرية محتمل",
        "تفسير وتأثير على القرار": "هذه المستويات تساعد فى تحديد مناطق الشراء قرب الدعوم ومناطق جنى الربح قرب المقاومات (استخدام تعليمى فقط).",
    })

    # 3) الاتجاه من MA20 / MA50
    rows.append({
        "المؤشر": "الاتجاه من MA20 / MA50",
        "القيمة": f"MA20 = {ma20:.2f} ، MA50 = {ma50:.2f}" if ma20 and ma50 else "غير متاح",
        "حالة السهم": trend_label,
        "تفسير وتأثير على القرار": trend_expl,
    })

    # 4) RSI
    rows.append({
        "المؤشر": "RSI (14)",
        "القيمة": f"{rsi_last:.2f}" if rsi_last is not None else "غير متاح",
        "حالة السهم": rsi_label,
        "تفسير وتأثير على القرار": rsi_expl,
    })

    # 5) التذبذب / النشاط
    rows.append({
        "المؤشر": "التذبذب اليومى / متوسط حجم 20 يوم",
        "القيمة": f"Range اليوم ≈ {row_intr.get('Range', np.nan):.2f}% | Vol20 ≈ {vol20_str or 'N/A'}",
        "حالة السهم": vol_label,
        "تفسير وتأثير على القرار": vol_expl,
    })

    # 6) سلوك الجلسة
    rows.append({
        "المؤشر": "سلوك الجلسة (Smart Money / معاملات اليوم)",
        "القيمة": (f"buy_ratio ≈ {buy_ratio_val:.2f}" if buy_ratio_val is not None else "غير متاح"),
        "حالة السهم": behavior_label,
        "تفسير وتأثير على القرار": behavior_expl,
    })

    df_indicators = pd.DataFrame(rows)
    st.dataframe(df_indicators, use_container_width=True)

    # -------- ملخص فنى آلى (Buy / Sell / Wait – تعليمى فقط) --------
    st.markdown("---")
    st.subheader("🧭 ملخص فنى آلى (ليس توصية استثمارية)")

    # تقييم عام (Rule-based تعليمى)
    decision = "انتظار / مراقبة"
    if trend_label == "اتجاه صاعد" and (change_pct is not None and change_pct > -1) \
       and behavior_label == "Accumulation" and (rsi_last is None or rsi_last < 70):
        decision = "شراء تعليمى على مراحل"
    elif rsi_last is not None and rsi_last > 70:
        decision = "جنى ربح / تخفيف تدريجى"
    elif trend_label == "اتجاه هابط" and behavior_label == "Distribution":
        decision = "انتظار / تجنب الشراء الجديد"

    st.write(f"**التوصية العامة:** {decision}")

    # مناطق سعرية تعليمية (Buy / Stop / Target) بناءً على الدعوم والمقاومات
    if np.isnan(last_price):
        st.info("لا يمكن حساب نقاط سعرية لعدم توفر سعر الإغلاق.")
    else:
        support_near = s1 if not np.isnan(s1) else (pivot - (pivot - s2) / 2 if not np.isnan(pivot) and not np.isnan(s2) else last_price * 0.97)
        stop_loss = s2 if not np.isnan(s2) else support_near * 0.97

        if not np.isnan(r1) and last_price < r1:
            target = r1
        elif not np.isnan(r2) and last_price <= r2:
            target = r2
        elif not np.isnan(r2):
            target = r2 * 1.03
        elif not np.isnan(r1):
            target = r1 * 1.03
        else:
            target = last_price * 1.05

        buy_low = min(last_price, support_near)
        buy_high = max(last_price, support_near)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.caption("نقطة شراء مقترحة (تعليمية)")
            st.metric(label="", value=f"{buy_low:.2f} - {buy_high:.2f}")
        with col_b2:
            st.caption("نقطة بيع / وقف تقريبية")
            st.metric(label="", value=f"{stop_loss:.2f}")
        with col_b3:
            st.caption("مستهدف سعرى تقريبى")
            st.metric(label="", value=f"{target:.2f}")

        st.markdown(
            "<small>هذه المستويات لأغراض تعليمية واختبار النموذج فقط، "
            "ولا تُعتبر توصية بيع أو شراء فعلية.</small>",
            unsafe_allow_html=True,
        )


# =========================================================
# 📉 صفحة S/R Breakouts
# =========================================================
elif page == "📉 S/R Breakouts":
    st.title("📉 S/R Breakouts – اختراقات الدعوم والمقاومات")

    if df_intraday is None or df_intraday.empty:
        st.warning("لا توجد بيانات Intraday متاحة.")
        st.stop()

    breakouts = utils.find_sr_breakouts(df_intraday)

    st.subheader("أسهم اخترقت المقاومة الأولى R1 (إغلاق ≥ R1)")
    st.dataframe(breakouts["R1_break"], use_container_width=True)

    st.subheader("أسهم اخترقت المقاومة الثانية R2 (إغلاق ≥ R2)")
    st.dataframe(breakouts["R2_break"], use_container_width=True)

    st.subheader("أسهم كسرت الدعم الأول S1 (إغلاق ≤ S1)")
    st.dataframe(breakouts["S1_break"], use_container_width=True)

    st.subheader("أسهم كسرت الدعم الثانى S2 (إغلاق ≤ S2)")
    st.dataframe(breakouts["S2_break"], use_container_width=True)


# =========================================================
# 🤖 AI Recommendations
# =========================================================
elif page == "🤖 AI Recommendations":
    st.title("🤖 AI Recommendations – إشارات الذكاء الاصطناعى")

    if signals is None or signals.empty:
        st.warning("لا توجد إشارات اليوم – تأكد من وجود ملفات intraday و transactions.")
        st.stop()

    df_sig = signals.copy()

    if "AI_Prob" not in df_sig.columns:
        df_sig["AI_Prob"] = 0.5

    df_sig = df_sig.sort_values("AI_Prob", ascending=False)

    st.subheader("أفضل الفرص وفق نموذج الذكاء الاصطناعى (الترتيب حسب AI_Prob)")
    st.dataframe(
        df_sig[["Symbol", "S. Description", "% Change", "Volume",
                "buy_ratio", "behavior", "AI_Prob"]],
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("📈 أسهم مناسبة للمضاربة T+0 / T+1 (تعليمى)")

    try:
        t0t1 = utils.build_t0_t1_candidates(df_sig, top_n=5)
        st.dataframe(t0t1, use_container_width=True)
    except Exception as e:
        st.error(f"تعذر حساب قائمة T+0 / T+1: {e}")

    # -------- علاقات الأسهم من CASE (تأثر متبادل) --------
    st.markdown("---")
    st.subheader("🔗 علاقات حركة الأسعار بين الأسهم (من CASE – تعليمى)")

    try:
        rel_df = utils.build_stock_relationships(
            intraday_df=df_intraday,
            min_days=60,
            min_abs_corr=0.7,
            top_n=40
        )

        if rel_df.empty:
            st.info("لا توجد بيانات كافية لحساب علاقات بين الأسهم.")
        else:
            pos_df = rel_df[rel_df["Relation"] == "Positive"]
            neg_df = rel_df[rel_df["Relation"] == "Negative"]

            st.markdown("#### أسهم تتحرك غالبًا فى نفس الاتجاه (علاقة طردية)")
            st.dataframe(pos_df, use_container_width=True)

            st.markdown("#### أسهم تتحرك غالبًا فى اتجاه معاكس (علاقة عكسية)")
            st.dataframe(neg_df, use_container_width=True)
    except Exception as e:
       st.error(f"خطأ أثناء حساب علاقات الأسهم من CASE: {e}")


    st.markdown(
        "<small>جميع الجداول أعلاه لأغراض تحليلية / تعليمية فقط، "
        "وليست توصية استثمارية أو دعوة لشراء أو بيع أى ورقة مالية.</small>",
        unsafe_allow_html=True,
    )


# =========================================================
# 📌 Group Picks Ranking
# =========================================================
elif page == "📌 Group Picks Ranking":
    st.title("📌 Group Picks Ranking – تقييم توصيات الجروبات")

    if signals is None or signals.empty:
        st.warning("لا توجد بيانات إشارات اليوم لاستخدامها فى التقييم.")
        st.stop()

    st.write("انسخ رموز الأسهم الموصى بها فى جروبات واتساب / تليجرام وضعها هنا (مسافات أو سطور أو فواصل):")

    text = st.text_area("رموز الأسهم:", height=150, value="")

    if st.button("تقييم التوصيات"):
        raw = text.replace(",", " ").replace("؛", " ").replace(";", " ")
        symbols_input = [s.strip() for s in raw.split() if s.strip()]
        symbols_input = list(dict.fromkeys(symbols_input))  # إزالة التكرار

        if not symbols_input:
            st.warning("لم يتم إدخال أى رموز.")
            st.stop()

        df_rank = utils.filter_group_picks(signals, symbols_input)
        if df_rank.empty:
            st.warning("لم يتم العثور على أى من هذه الرموز فى بيانات اليوم.")
            st.stop()

        st.subheader("ترتيب توصيات الجروبات حسب قوة الإشارة (AI_Prob)")
        st.dataframe(df_rank, use_container_width=True)

        st.subheader("رسم بيانى لاحتمالات النجاح (AI_Prob)")
        st.bar_chart(df_rank.set_index("Symbol")["AI_Prob"])


# =========================================================
# 🧠 AI & News Analytics
# =========================================================
elif page == "🧠 AI & News Analytics":
    st.title("🧠 AI & News Analytics – تحليلات الأخبار والذكاء الاصطناعى")

    st.info(
        "فى هذه الصفحة سيتم مستقبلاً ربط الأخبار من EGX، مباشر، ميست نيوز، المال، البورصة نيوز، "
        "وتحليل تأثيرها على الأسهم. حالياً يمكنك رفع ملف أخبار CSV لتجربته."
    )

    uploaded = st.file_uploader(
        "ارفع ملف أخبار (CSV) يحتوى على الأعمدة: Datetime, Symbol, Headline, Sentiment",
        type=["csv"]
    )
    if uploaded is not None:
        try:
            df_news = pd.read_csv(uploaded)
            st.dataframe(df_news.head(), use_container_width=True)
        except Exception as e:
            st.error(f"خطأ أثناء قراءة ملف الأخبار: {e}")
