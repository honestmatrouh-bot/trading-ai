from pathlib import Path
import pandas as pd
import numpy as np

# =========================
# مسارات رئيسية
# =========================
BASE_DIR = Path(__file__).resolve().parent
CASE_DIR = BASE_DIR / "CASE"
INTRADAY_DIR = BASE_DIR / "intraday"
TRANSACTION_DIR = BASE_DIR / "transaction"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# مؤشرات السوق العامة (لا نعرضها وسط الأسهم)
INDEX_SYMBOLS = {
    "EGX30", "EGX70", "EGX100",
    "EGX100 EWI", "EGX70 EWI",
    "EGX30ETF", "EGX30TR",
    "SHARIAH", "EGX33 Shariah Index"
}


# =========================
# دوال مساعدة لتطبيع الأعمدة
# =========================

def normalize_intraday_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ترجمة الأعمدة العربية للإنجليزية وتوحيد الأسماء."""
    df = df.copy()

    rename_map = {
        "الرمز": "Symbol",
        "الإسم المختصر": "S. Description",
        "الاسم المختصر": "S. Description",
        "أخر سعر": "Last",
        "آخر سعر": "Last",
        "التغير %": "% Change",
        "حجم التداول": "Volume",
        "قيمة التداول": "Turnover",
        "حجم السيولة الداخلة": "Cash In Volume",
        "حجم السيولة الخارجة": "Cash Out Volume",
        "الصفقات": "Trades",
        "مخطط السيولة %": "Range",  # بعض البرامج تستخدمها لنسبة مدى الحركة
        "(R1) المقاومة 1": "Resistance 1 (R1)",
        "(R2) المقاومة 2": "Resistance 2 (R2)",
        "(S1) الدعم 1": "Support 1 (S1)",
        "(S2) الدعم 2": "Support 2 (S2)",
        "الأدنى": "Low",
        "أعلى": "High",
        "فتح": "Open",
        "إغلاق": "Close",
        "الأدنى خلال 52 أسبوع": "52 week Low",
        "الأعلى خلال 52 أسبوع": "52 week High",
        "نسبة الطلب على العرض": "Bid Offer Ratio",
        "الطلب": "Bid",
        "العرض": "Offer",
        "كمية الطلب": "Bid Qty.",
        "كمية العرض": "Offer Qty.",
        "القطاع": "Sector",
        "مضاعف ربحية السهم": "P-E Ratio",
        "مضاعف القيمة الدفترية": "P-B Ratio",
        "ربحية السهم": "Earning Per Share",
        "% المدى": "Range",
        "صفقات السيولة الداخلة": "Cash In Trades",
        "صفقات السيولة الخارجة": "Cash Out Trades",
        "قيمة السيولة الخارجة": "Cash Out Turnover",
        "قيمة السيولة الداخلة": "Cash in Turnover",  # نستخدم نفس الاسم فى app
        "مؤشر السيولة النقدية": "Cash Flow Index",
        "نقطة الإرتكاز": "Pivot Point",
        "رسملة السوق بالآلاف": "Mkt. Cap./1000",
        "تغير متوسط السعر المرجح %": "VWAP Change",
        "إقفال سابق": "Prev. Closed",
        "نسبة السيولة": "Cash Map % Value",
        "S. Description": "S. Description",  # لو هى بالفعل إنجليزى
    }
    df = df.rename(columns=rename_map)

    # 🔧 أهم تعديل: إزالة الأعمدة المكررة بعد التسمية
    # لو كان عندك "أخر سعر" و"آخر سعر" الاتنين بقوا Last -> نحافظ على أول واحد
    df = df.loc[:, ~df.columns.duplicated()]

    return df


def normalize_transactions_columns(df: pd.DataFrame) -> pd.DataFrame:
    """توحيد أعمدة ملف معاملات الجلسة."""
    df = df.copy()

    rename_map = {
        "اسم السهم": "Description",
        "الإسم المختصر": "Description",
        "الاسم": "Description",
        "الرمز": "Symbol",
        "السعر": "Price",
        "النوع": "Side",     # B / S أو Buy / Sell
        "التغير %": "% Change",
        "حجم التداول": "Volume",
        "قيمة التداول": "Turnover",
        "مُعرف التسلسل": "Sequence ID",
        "الوقت": "Time",
        "Tick": "Tick",
        "إتجاه": "Direction",   # 2 / 1 / -2 ... الخ
        "اتجاه": "Direction",
    }
    df = df.rename(columns=rename_map)
    df = df.loc[:, ~df.columns.duplicated()]

    # تأكد من وجود الأعمدة المهمة
    for col in ["Symbol", "Side", "Volume", "Turnover"]:
        if col not in df.columns:
            df[col] = np.nan
    return df


def normalize_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    """توحيد أعمدة ملفات CASE التاريخية."""
    df = df.copy()

    rename_map = {
        "التاريخ": "Date",
        "فتح": "Open",
        "أعلى": "High",
        "الأدنى": "Low",
        "مغلق": "Closed",
        "إقفال سابق": "Prev. Closed",
        "التغير %": "%Chg",
        "التغير": "Chg.",
        "قيمة التداول": "Turnover",
        "حجم التداول": "Volume",
    }
    df = df.rename(columns=rename_map)
    df = df.loc[:, ~df.columns.duplicated()]

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    return df


# =========================
# تحميل البيانات الأساسية
# =========================

def load_intraday(path: Path) -> pd.DataFrame:
    """قراءة ملف intraday (XLSX) مع تحديد openpyxl كـ engine."""
    df = pd.read_excel(path, engine="openpyxl")
    df = normalize_intraday_columns(df)

    core = ["Symbol", "S. Description", "Last", "% Change", "Open", "High", "Low", "Volume"]
    missing = [c for c in core if c not in df.columns]
    if missing:
        print("⚠️ Intraday missing core columns:", missing)

    # نحاول تحويل بعض الأعمدة المهمة لأرقام
    for c in ["Last", "% Change", "Open", "High", "Low", "Close", "Prev. Closed",
              "Range", "Volume", "Turnover"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # حساب مستويات Pivot لو ناقصة / فيها NaN
    df = add_pivot_levels(df)

    return df


def load_transactions(path: Path) -> pd.DataFrame:
    """قراءة ملف معاملات الجلسة مع تجربة أكثر من ترميز."""
    encodings_to_try = ["utf-8-sig", "utf-16", "cp1256", "cp1252"]

    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(path, encoding=enc)
            df = normalize_transactions_columns(df)
            print(f"Loaded transactions using encoding: {enc}")
            break
        except Exception:
            df = None

    if df is None:
        df = pd.read_csv(path, encoding="latin1", errors="replace")
        df = normalize_transactions_columns(df)
        print("⚠️ Loaded transactions with fallback encoding (latin1 with replacement).")

    # تحويل أرقام
    for c in ["Price", "% Change", "Volume", "Turnover"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def load_case(symbol: str) -> pd.DataFrame:
    """قراءة ملف CASE التاريخى لسهم معين مع دعم ترميزات عربية."""
    path = CASE_DIR / f"{symbol}.csv"

    encodings_to_try = ["utf-8-sig", "utf-16", "cp1256", "cp1252"]
    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(path, encoding=enc)
            df = normalize_case_columns(df)
            print(f"Loaded CASE for {symbol} using encoding: {enc}")
            break
        except Exception:
            df = None

    if df is None:
        df = pd.read_csv(path, encoding="latin1", errors="replace")
        df = normalize_case_columns(df)
        print(f"⚠️ Loaded CASE for {symbol} with fallback encoding (latin1 with replacement).")

    # تأكد من أن الإغلاق أرقام
    for c in ["Open", "High", "Low", "Closed", "Prev. Closed", "Turnover", "Volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


# =========================
# تحليلات معاملات الجلسة
# =========================

def aggregate_transactions(df_tx: pd.DataFrame) -> pd.DataFrame:
    """تلخيص معاملات الجلسة لكل سهم (حجم، سيولة، تجميع/تصريف)."""
    if df_tx is None or df_tx.empty:
        return pd.DataFrame(columns=["Symbol", "total_volume", "total_turnover",
                                     "buy_volume", "sell_volume", "buy_ratio",
                                     "behavior"])

    df = df_tx.copy()
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)
    df["Turnover"] = pd.to_numeric(df["Turnover"], errors="coerce").fillna(0)

    # تحديد عمليات الشراء والبيع:
    side = df["Side"].astype(str).str.upper()

    buy_mask = side.isin(["B", "BUY"])
    sell_mask = side.isin(["S", "SELL"])

    # لو مفيش معلومات فى Side نحاول نستفيد من Direction (2 / -2 / 1...)
    if (not buy_mask.any()) and ("Direction" in df.columns):
        dir_col = pd.to_numeric(df["Direction"], errors="coerce")
        buy_mask = dir_col.gt(0)
        sell_mask = dir_col.lt(0)

    grouped = df.groupby("Symbol")

    total_volume = grouped["Volume"].sum()
    total_turnover = grouped["Turnover"].sum()
    buy_volume = df[buy_mask].groupby("Symbol")["Volume"].sum()
    sell_volume = df[sell_mask].groupby("Symbol")["Volume"].sum()

    agg = pd.DataFrame({
        "total_volume": total_volume,
        "total_turnover": total_turnover,
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
    }).fillna(0)

    agg["buy_ratio"] = agg.apply(
        lambda r: r["buy_volume"] / r["total_volume"] if r["total_volume"] > 0 else np.nan,
        axis=1
    )

    def classify_behavior(row):
        if np.isnan(row["buy_ratio"]):
            return "Normal"
        if row["buy_ratio"] > 0.6:
            return "Accumulation"
        if row["buy_ratio"] < 0.4:
            return "Distribution"
        return "Normal"

    agg["behavior"] = agg.apply(classify_behavior, axis=1)

    agg.reset_index(inplace=True)
    return agg


# =========================
# مؤشرات فنية أساسية من CASE
# =========================

def compute_basic_technicals(df_case: pd.DataFrame) -> pd.DataFrame:
    """
    حساب إغلاق اليوم، MA20، MA50، متوسط حجم 20 يوم.
    يرجع صفاً واحداً يمثل آخر يوم.
    """
    df = df_case.sort_values("Date").copy()

    if "Closed" in df.columns:
        close = pd.to_numeric(df["Closed"], errors="coerce")
    elif "Close" in df.columns:
        close = pd.to_numeric(df["Close"], errors="coerce")
    else:
        raise ValueError("لا يوجد عمود Closed/Close فى بيانات CASE.")

    df["Close_val"] = close
    df["MA20"] = df["Close_val"].rolling(20).mean()
    df["MA50"] = df["Close_val"].rolling(50).mean()

    if "Volume" in df.columns:
        df["Vol20"] = pd.to_numeric(df["Volume"], errors="coerce").rolling(20).mean()
    else:
        df["Vol20"] = np.nan

    last_row = df.iloc[[-1]][["Close_val", "MA20", "MA50", "Vol20"]]
    last_row.rename(columns={"Close_val": "Close"}, inplace=True)
    return last_row


# =========================
# حساب Pivot / R1 / R2 / S1 / S2
# =========================

def add_pivot_levels(df_intraday: pd.DataFrame) -> pd.DataFrame:
    """
    ضمان وجود الأعمدة:
      Pivot Point, Resistance 1 (R1), Resistance 2 (R2),
      Support 1 (S1), Support 2 (S2)
    لو غير موجودة أو مليانة NaN نحسبها من:
      P = (High + Low + Prev. Closed) / 3
    """
    df = df_intraday.copy()

    # نتأكد أن الأعمدة موجودة
    if "Pivot Point" not in df.columns:
        df["Pivot Point"] = np.nan
    if "Resistance 1 (R1)" not in df.columns:
        df["Resistance 1 (R1)"] = np.nan
    if "Resistance 2 (R2)" not in df.columns:
        df["Resistance 2 (R2)"] = np.nan
    if "Support 1 (S1)" not in df.columns:
        df["Support 1 (S1)"] = np.nan
    if "Support 2 (S2)" not in df.columns:
        df["Support 2 (S2)"] = np.nan

    high = pd.to_numeric(df.get("High"), errors="coerce")
    low = pd.to_numeric(df.get("Low"), errors="coerce")

    # نستخدم إقفال سابق كـ Close للحساب، لو مش موجود نستخدم Last
    if "Prev. Closed" in df.columns:
        close_for_pivot = pd.to_numeric(df["Prev. Closed"], errors="coerce")
    else:
        close_for_pivot = pd.to_numeric(df.get("Last"), errors="coerce")

    # pivot / R / S
    mask_valid = (~high.isna()) & (~low.isna()) & (~close_for_pivot.isna())

    # نحسب فقط للأماكن اللى فيها NaN أو القيم كلها صفر
    need_calc = mask_valid & (
        df["Pivot Point"].isna()
        & df["Resistance 1 (R1)"].isna()
        & df["Resistance 2 (R2)"].isna()
        & df["Support 1 (S1)"].isna()
        & df["Support 2 (S2)"].isna()
    )

    P = (high + low + close_for_pivot) / 3.0
    R1 = 2 * P - low
    S1 = 2 * P - high
    R2 = P + (high - low)
    S2 = P - (high - low)

    df.loc[need_calc, "Pivot Point"] = P[need_calc]
    df.loc[need_calc, "Resistance 1 (R1)"] = R1[need_calc]
    df.loc[need_calc, "Resistance 2 (R2)"] = R2[need_calc]
    df.loc[need_calc, "Support 1 (S1)"] = S1[need_calc]
    df.loc[need_calc, "Support 2 (S2)"] = S2[need_calc]

    return df


# =========================
# بناء جدول الإشارات اليومية
# =========================

def build_signals_for_day(intraday_path: Path, tx_path: Path) -> pd.DataFrame:
    """دمج بيانات intraday مع ملخص معاملات الجلسة لإنتاج جدول إشارات."""
    df_intraday = load_intraday(intraday_path)
    df_tx = load_transactions(tx_path)
    agg_tx = aggregate_transactions(df_tx)

    df = df_intraday.merge(agg_tx, on="Symbol", how="left")

    # سيولة دخول/خروج لو مش موجودة
    if "Cash in Turnover" not in df.columns:
        df["Cash in Turnover"] = df["total_turnover"].fillna(0)
    if "Cash Out Turnover" not in df.columns:
        df["Cash Out Turnover"] = 0

    return df


# =========================
# "نموذج" ذكاء اصطناعى مبدئى Rule-based
# =========================

def apply_ai_score(signals: pd.DataFrame) -> pd.DataFrame:
    """
    حساب درجة احتمالية نجاح الفرصة (AI_Prob) بناءً على قواعد بسيطة:
    - اتجاه حركة السعر (% Change)
    - buy_ratio (من معاملات الجلسة)
    - سلوك الجلسة (Accumulation/Distribution)
    """
    df = signals.copy()

    if "AI_Prob" in df.columns:
        return df

    df["AI_Prob"] = 0.5

    # تأثير التغير اليومى
    if "% Change" in df.columns:
        change = pd.to_numeric(df["% Change"], errors="coerce").fillna(0)
        df["AI_Prob"] += np.where(change > 0, 0.07, np.where(change < 0, -0.07, 0))

    # تأثير buy_ratio
    if "buy_ratio" in df.columns:
        br = pd.to_numeric(df["buy_ratio"], errors="coerce")
        df["AI_Prob"] += 0.3 * (br - 0.5).fillna(0)

    # سلوك الجلسة
    if "behavior" in df.columns:
        df["AI_Prob"] += df["behavior"].map({
            "Accumulation": 0.08,
            "Distribution": -0.08
        }).fillna(0)

    # قص القيم بين 0.05 و 0.95
    df["AI_Prob"] = df["AI_Prob"].clip(0.05, 0.95)

    return df


# =========================
# S/R Breakouts helper
# =========================

def find_sr_breakouts(df_intraday: pd.DataFrame):
    """
    تحديد الأسهم التى:
    - أغلقت فوق R1 أو R2
    - أغلقت تحت S1 أو S2
    نعتمد على Last كسعر الجلسة.
    """
    df = add_pivot_levels(df_intraday)

    price = pd.to_numeric(df.get("Last"), errors="coerce")
    r1 = pd.to_numeric(df.get("Resistance 1 (R1)"), errors="coerce")
    r2 = pd.to_numeric(df.get("Resistance 2 (R2)"), errors="coerce")
    s1 = pd.to_numeric(df.get("Support 1 (S1)"), errors="coerce")
    s2 = pd.to_numeric(df.get("Support 2 (S2)"), errors="coerce")

    cols_basic = ["Symbol", "S. Description", "Last", "% Change",
                  "Volume", "Resistance 1 (R1)", "Resistance 2 (R2)",
                  "Support 1 (S1)", "Support 2 (S2)"]

    r1_break = df[(price >= r1) & r1.notna()][cols_basic]
    r2_break = df[(price >= r2) & r2.notna()][cols_basic]
    s1_break = df[(price <= s1) & s1.notna()][cols_basic]
    s2_break = df[(price <= s2) & s2.notna()][cols_basic]

    return {
        "R1_break": r1_break.sort_values("% Change", ascending=False),
        "R2_break": r2_break.sort_values("% Change", ascending=False),
        "S1_break": s1_break.sort_values("% Change", ascending=True),
        "S2_break": s2_break.sort_values("% Change", ascending=True),
    }


# =========================
# T+0 / T+1 candidates
# =========================

def build_t0_t1_candidates(signals: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    اختيار أسهم مناسبة للمضاربة القصيرة T+0 / T+1:
    - تذبذب (Range) عالى
    - حجم تداول جيد
    - سيولة مركزة (buy_ratio قريب من 0.5 – 0.7)
    - AI_Prob جيد
    """
    df = signals.copy()

    # Range: لو غير موجود، نحسبه تقريبيا من (High-Low)/Last
    if "Range" in df.columns:
        rng = pd.to_numeric(df["Range"], errors="coerce")
    else:
        high = pd.to_numeric(df.get("High"), errors="coerce")
        low = pd.to_numeric(df.get("Low"), errors="coerce")
        last = pd.to_numeric(df.get("Last"), errors="coerce")
        rng = (high - low) / last.replace(0, np.nan) * 100
    df["Range_calc"] = rng

    vol = pd.to_numeric(df.get("Volume"), errors="coerce").fillna(0)
    ai_prob = pd.to_numeric(df.get("AI_Prob"), errors="coerce").fillna(0.5)
    buy_ratio = pd.to_numeric(df.get("buy_ratio"), errors="coerce")

    # فلترة مبدئية
    mask = (vol >= vol.quantile(0.5)) & (df["Range_calc"] >= df["Range_calc"].quantile(0.5))
    cand = df[mask].copy()

    # درجة T0/T1
    cand["T0T1_Score"] = (
        100 * ai_prob +
        3 * cand["Range_calc"].fillna(0) +
        50 * (buy_ratio.fillna(0.5) - 0.5)
    )

    cols = ["Symbol", "S. Description", "Last", "% Change", "Volume",
            "Range_calc", "buy_ratio", "behavior", "AI_Prob", "T0T1_Score"]
    cols = [c for c in cols if c in cand.columns]

    cand = cand.sort_values("T0T1_Score", ascending=False).head(top_n)
    return cand[cols]


# =========================
# علاقات الأسهم من CASE (Correlation)
# =========================

def build_stock_relationships(
    intraday_df: pd.DataFrame,
    min_days: int = 60,
    min_abs_corr: float = 0.7,
    top_n: int = 40
) -> pd.DataFrame:
    """
    حساب علاقات (Correlation) بين عوائد الأسهم المعروضة فى جلسة اليوم
    اعتماداً على بيانات CASE (إغلاق يومى).
    - نختار top_n أسهم من حيث حجم التداول فى intraday
    - نحسب العائد اليومى (نسبة التغير) لكل سهم
    - نبنى مصفوفة ارتباط
    - نخرج الأزواج ذات |corr| >= min_abs_corr
    """
    if intraday_df is None or intraday_df.empty:
        return pd.DataFrame(columns=["Symbol_A", "Symbol_B", "Corr", "Relation"])

    df_intra = intraday_df.copy()
    if "Volume" in df_intra.columns:
        df_intra["Volume"] = pd.to_numeric(df_intra["Volume"], errors="coerce").fillna(0)
        df_intra = df_intra.sort_values("Volume", ascending=False)
    symbols = df_intra["Symbol"].astype(str).dropna().unique().tolist()
    symbols = symbols[:top_n]

    returns_dict = {}
    for sym in symbols:
        try:
            df_case = load_case(sym)
            if df_case.empty:
                continue
            df_case = df_case.sort_values("Date")
            if "Closed" in df_case.columns:
                close = pd.to_numeric(df_case["Closed"], errors="coerce")
            elif "Close" in df_case.columns:
                close = pd.to_numeric(df_case["Close"], errors="coerce")
            else:
                continue
            ret = close.pct_change()
            ret.name = sym
            returns_dict[sym] = ret
        except FileNotFoundError:
            continue
        except Exception:
            continue

    if not returns_dict:
        return pd.DataFrame(columns=["Symbol_A", "Symbol_B", "Corr", "Relation"])

    # دمج كل السلاسل على تاريخ مشترك
    returns_df = pd.concat(returns_dict.values(), axis=1, join="inner").dropna(how="all")
    if len(returns_df) < min_days:
        # لو البيانات قليلة جدًا
        return pd.DataFrame(columns=["Symbol_A", "Symbol_B", "Corr", "Relation"])

    corr_mat = returns_df.corr()

    rows = []
    syms = corr_mat.columns.tolist()
    for i in range(len(syms)):
        for j in range(i + 1, len(syms)):
            a = syms[i]
            b = syms[j]
            c = corr_mat.loc[a, b]
            if pd.isna(c):
                continue
            if abs(c) >= min_abs_corr:
                rel = "Positive" if c > 0 else "Negative"
                rows.append({"Symbol_A": a, "Symbol_B": b, "Corr": float(c), "Relation": rel})

    if not rows:
        return pd.DataFrame(columns=["Symbol_A", "Symbol_B", "Corr", "Relation"])

    rel_df = pd.DataFrame(rows)
    rel_df["AbsCorr"] = rel_df["Corr"].abs()
    rel_df = rel_df.sort_values("AbsCorr", ascending=False)

    # نعيد فقط أعمدة العرض
    rel_df = rel_df[["Symbol_A", "Symbol_B", "Corr", "Relation"]]
    return rel_df


# =========================
# Group Picks helper
# =========================

def filter_group_picks(signals: pd.DataFrame, symbols_list) -> pd.DataFrame:
    """
    فلترة جدول الإشارات بناءً على قائمة رموز من جروبات التوصيات،
    وإرجاعها مرتبة تنازلياً حسب AI_Prob.
    """
    df = signals.copy()
    df["Symbol"] = df["Symbol"].astype(str)
    mask = df["Symbol"].isin(symbols_list)
    df = df[mask].copy()

    if "AI_Prob" not in df.columns:
        df["AI_Prob"] = 0.5

    cols_show = ["Symbol", "S. Description", "% Change", "Volume",
                 "buy_ratio", "behavior", "AI_Prob"]
    cols_show = [c for c in cols_show if c in df.columns]

    df = df.sort_values("AI_Prob", ascending=False)
    return df[cols_show]
