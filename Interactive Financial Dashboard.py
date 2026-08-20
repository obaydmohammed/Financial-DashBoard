import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------
# Financial Analytics Dashboard
# Python + Tkinter + Pandas + Matplotlib + yFinance
# ---------------------------------------------------------

BG = "#0b0f14"
PANEL = "#11161d"
PANEL_2 = "#151b23"
BORDER = "#202833"
TEXT = "#f1f5f9"
MUTED = "#7f8da0"
ACCENT = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#f59e0b"

root = tk.Tk()
root.title("Financial Analytics Dashboard")
root.geometry("1400x850")
root.minsize(1100, 700)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TCombobox",
    fieldbackground=PANEL_2,
    background=PANEL_2,
    foreground=TEXT,
    bordercolor=BORDER,
    arrowcolor=TEXT,
    padding=7,
)

style.configure(
    "TButton",
    background=PANEL_2,
    foreground=TEXT,
    bordercolor=BORDER,
    padding=(12, 7),
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def format_number(value):
    if value is None or pd.isna(value):
        return "N/A"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:,.0f}"


def money(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"${float(value):,.2f}"


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


# ---------------------------------------------------------
# Data
# ---------------------------------------------------------

def get_data(ticker, period):
    stock = yf.Ticker(ticker)

    data = stock.history(
        period=period,
        interval="1d",
        auto_adjust=True
    )

    if data.empty:
        raise ValueError("No market data was found for this ticker.")

    data = data.reset_index()

    data["SMA20"] = data["Close"].rolling(20).mean()
    data["SMA50"] = data["Close"].rolling(50).mean()

    data["DailyReturn"] = (
        data["Close"].pct_change() * 100
    )

    data["Volatility"] = (
        data["DailyReturn"].rolling(20).std()
    )

    return stock, data


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=28, pady=(22, 10))

title_frame = tk.Frame(header, bg=BG)
title_frame.pack(side="left")

tk.Label(
    title_frame,
    text="FINANCIAL",
    font=("Segoe UI", 20, "bold"),
    fg=ACCENT,
    bg=BG,
).pack(side="left")

tk.Label(
    title_frame,
    text=" ANALYTICS",
    font=("Segoe UI", 20, "bold"),
    fg=TEXT,
    bg=BG,
).pack(side="left")

tk.Label(
    title_frame,
    text="Interactive market intelligence",
    font=("Segoe UI", 10),
    fg=MUTED,
    bg=BG,
).pack(anchor="w", pady=(3, 0))


controls = tk.Frame(header, bg=BG)
controls.pack(side="right")

tk.Label(
    controls,
    text="TICKER",
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=BG,
).pack(side="left", padx=(0, 6))

ticker_var = tk.StringVar(value="AAPL")

ticker_entry = tk.Entry(
    controls,
    textvariable=ticker_var,
    width=10,
    font=("Segoe UI", 11, "bold"),
    bg=PANEL_2,
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
)
ticker_entry.pack(side="left", padx=(0, 8), ipady=7)

period_var = tk.StringVar(value="1 Year")

period_box = ttk.Combobox(
    controls,
    textvariable=period_var,
    values=["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years"],
    state="readonly",
    width=11,
)
period_box.pack(side="left", padx=(0, 8))

refresh_button = tk.Button(
    controls,
    text="Analyze",
    command=lambda: load_dashboard(),
    bg=ACCENT,
    fg="#061018",
    activebackground=ACCENT,
    activeforeground="#061018",
    relief="flat",
    cursor="hand2",
    font=("Segoe UI", 10, "bold"),
    padx=15,
    pady=7,
)
refresh_button.pack(side="left")


# ---------------------------------------------------------
# Company heading
# ---------------------------------------------------------

company_frame = tk.Frame(root, bg=BG)
company_frame.pack(fill="x", padx=28, pady=(8, 15))

company_label = tk.Label(
    company_frame,
    text="Apple Inc.",
    font=("Segoe UI", 17, "bold"),
    fg=TEXT,
    bg=BG,
)
company_label.pack(side="left")

ticker_label = tk.Label(
    company_frame,
    text="AAPL",
    font=("Segoe UI", 10, "bold"),
    fg=ACCENT,
    bg=BG,
)
ticker_label.pack(side="left", padx=10)


trend_label = tk.Label(
    company_frame,
    text="● Neutral",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=BG,
)
trend_label.pack(side="right")


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

kpi_container = tk.Frame(root, bg=BG)
kpi_container.pack(fill="x", padx=28)

kpi_data = {}

for i in range(6):
    card = tk.Frame(
        kpi_container,
        bg=PANEL,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    card.grid(
        row=0,
        column=i,
        sticky="nsew",
        padx=(0 if i == 0 else 7, 0),
    )

    kpi_container.columnconfigure(i, weight=1)

    labels = [
        "CURRENT PRICE",
        "DAILY CHANGE",
        "PERIOD HIGH",
        "PERIOD LOW",
        "VOLUME",
        "VOLATILITY",
    ]

    key = labels[i]

    tk.Label(
        card,
        text=key,
        font=("Segoe UI", 8, "bold"),
        fg=MUTED,
        bg=PANEL,
    ).pack(anchor="w", padx=15, pady=(13, 5))

    value = tk.Label(
        card,
        text="—",
        font=("Segoe UI", 17, "bold"),
        fg=TEXT,
        bg=PANEL,
    )
    value.pack(anchor="w", padx=15)

    sub = tk.Label(
        card,
        text="",
        font=("Segoe UI", 8),
        fg=MUTED,
        bg=PANEL,
    )
    sub.pack(anchor="w", padx=15, pady=(3, 13))

    kpi_data[key] = (value, sub)


# ---------------------------------------------------------
# Main content
# ---------------------------------------------------------

content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=28, pady=18)

left = tk.Frame(
    content,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1,
)
left.pack(side="left", fill="both", expand=True, padx=(0, 10))

right = tk.Frame(
    content,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1,
    width=330,
)
right.pack(side="right", fill="y")

right.pack_propagate(False)


# ---------------------------------------------------------
# Chart
# ---------------------------------------------------------

chart_header = tk.Frame(left, bg=PANEL)
chart_header.pack(fill="x", padx=18, pady=(15, 0))

tk.Label(
    chart_header,
    text="PRICE PERFORMANCE",
    font=("Segoe UI", 10, "bold"),
    fg=TEXT,
    bg=PANEL,
).pack(side="left")

tk.Label(
    chart_header,
    text="Closing price and moving averages",
    font=("Segoe UI", 8),
    fg=MUTED,
    bg=PANEL,
).pack(side="left", padx=12)


figure = Figure(
    figsize=(8, 5),
    dpi=100,
    facecolor=PANEL,
)

ax = figure.add_subplot(111)
ax.set_facecolor(PANEL)

canvas = FigureCanvasTkAgg(
    figure,
    master=left,
)

canvas.get_tk_widget().pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10,
)


# ---------------------------------------------------------
# Right analytics panel
# ---------------------------------------------------------

tk.Label(
    right,
    text="ANALYTICS",
    font=("Segoe UI", 10, "bold"),
    fg=TEXT,
    bg=PANEL,
).pack(anchor="w", padx=20, pady=(18, 3))

tk.Label(
    right,
    text="Key market indicators",
    font=("Segoe UI", 8),
    fg=MUTED,
    bg=PANEL,
).pack(anchor="w", padx=20)


def create_metric(title):
    frame = tk.Frame(
        right,
        bg=PANEL_2,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    frame.pack(fill="x", padx=18, pady=7)

    tk.Label(
        frame,
        text=title,
        font=("Segoe UI", 8),
        fg=MUTED,
        bg=PANEL_2,
    ).pack(anchor="w", padx=12, pady=(10, 2))

    value = tk.Label(
        frame,
        text="—",
        font=("Segoe UI", 13, "bold"),
        fg=TEXT,
        bg=PANEL_2,
    )
    value.pack(anchor="w", padx=12, pady=(0, 10))

    return value


market_cap_value = create_metric("MARKET CAP")
pe_value = create_metric("P/E RATIO")
avg_volume_value = create_metric("AVG. VOLUME")
return_value = create_metric("LATEST DAILY RETURN")


tk.Label(
    right,
    text="TREND SIGNAL",
    font=("Segoe UI", 8, "bold"),
    fg=MUTED,
    bg=PANEL,
).pack(anchor="w", padx=20, pady=(20, 5))


signal_frame = tk.Frame(
    right,
    bg=PANEL_2,
)
signal_frame.pack(fill="x", padx=18)

signal_value = tk.Label(
    signal_frame,
    text="NEUTRAL",
    font=("Segoe UI", 14, "bold"),
    fg=YELLOW,
    bg=PANEL_2,
)
signal_value.pack(pady=(14, 3))

signal_description = tk.Label(
    signal_frame,
    text="Waiting for market data...",
    font=("Segoe UI", 8),
    fg=MUTED,
    bg=PANEL_2,
    wraplength=260,
    justify="center",
)
signal_description.pack(
    padx=12,
    pady=(0, 14),
)


# ---------------------------------------------------------
# Bottom charts
# ---------------------------------------------------------

bottom = tk.Frame(root, bg=BG)
bottom.pack(fill="x", padx=28, pady=(0, 18))

volume_panel = tk.Frame(
    bottom,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1,
)
volume_panel.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10),
)

return_panel = tk.Frame(
    bottom,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1,
)
return_panel.pack(
    side="right",
    fill="both",
    expand=True,
)


def create_small_chart(panel, title):
    tk.Label(
        panel,
        text=title,
        font=("Segoe UI", 9, "bold"),
        fg=TEXT,
        bg=PANEL,
    ).pack(anchor="w", padx=15, pady=(10, 0))

    fig = Figure(
        figsize=(6, 2),
        dpi=90,
        facecolor=PANEL,
    )

    axis = fig.add_subplot(111)
    axis.set_facecolor(PANEL)

    c = FigureCanvasTkAgg(
        fig,
        master=panel,
    )

    c.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=8,
        pady=5,
    )

    return fig, axis, c


volume_fig, volume_ax, volume_canvas = create_small_chart(
    volume_panel,
    "TRADING VOLUME",
)

return_fig, return_ax, return_canvas = create_small_chart(
    return_panel,
    "DAILY RETURNS",
)


# ---------------------------------------------------------
# Chart styling
# ---------------------------------------------------------

def style_axis(axis):
    axis.tick_params(
        colors=MUTED,
        labelsize=7,
    )

    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    axis.spines["left"].set_color(BORDER)
    axis.spines["bottom"].set_color(BORDER)

    axis.grid(
        True,
        alpha=0.12,
        color="#64748b",
    )


# ---------------------------------------------------------
# Dashboard loading
# ---------------------------------------------------------

def period_to_yfinance(period):
    return {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y",
    }[period]


def load_dashboard():
    ticker = ticker_var.get().strip().upper()

    if not ticker:
        messagebox.showwarning(
            "Missing ticker",
            "Please enter a stock ticker."
        )
        return

    period = period_to_yfinance(
        period_var.get()
    )

    refresh_button.config(
        text="Loading...",
        state="disabled"
    )

    root.update_idletasks()

    try:
        stock, data = get_data(
            ticker,
            period
        )

        update_dashboard(
            ticker,
            stock,
            data
        )

    except Exception as error:

        messagebox.showerror(
            "Unable to load data",
            str(error)
        )

    finally:

        refresh_button.config(
            text="Analyze",
            state="normal"
        )


def update_dashboard(ticker, stock, data):

    info = stock.info

    latest = data.iloc[-1]

    previous = (
        data.iloc[-2]["Close"]
        if len(data) > 1
        else latest["Close"]
    )

    change = latest["Close"] - previous

    change_pct = (
        change / previous * 100
        if previous
        else 0
    )

    high = data["High"].max()
    low = data["Low"].min()

    volume = latest["Volume"]

    volatility = (
        latest["Volatility"]
        if pd.notna(latest["Volatility"])
        else 0
    )

    # Company name

    company = info.get(
        "longName",
        ticker
    )

    company_label.config(
        text=company
    )

    ticker_label.config(
        text=ticker
    )

    # KPIs

    kpi_data["CURRENT PRICE"][0].config(
        text=money(latest["Close"])
    )

    change_text = (
        f"{'+' if change_pct >= 0 else ''}"
        f"{change_pct:.2f}%"
    )

    kpi_data["DAILY CHANGE"][0].config(
        text=change_text,
        fg=GREEN if change_pct >= 0 else RED
    )

    kpi_data["DAILY CHANGE"][1].config(
        text=(
            f"{'+' if change >= 0 else ''}"
            f"{money(change)} today"
        )
    )

    kpi_data["PERIOD HIGH"][0].config(
        text=money(high)
    )

    kpi_data["PERIOD LOW"][0].config(
        text=money(low)
    )

    kpi_data["VOLUME"][0].config(
        text=format_number(volume)
    )

    kpi_data["VOLUME"][1].config(
        text="Latest session"
    )

    kpi_data["VOLATILITY"][0].config(
        text=f"{volatility:.2f}%"
    )

    kpi_data["VOLATILITY"][1].config(
        text="20-day standard deviation"
    )

    # Analytics

    market_cap = info.get(
        "marketCap"
    )

    pe = info.get(
        "trailingPE"
    )

    avg_volume = data["Volume"].mean()

    latest_return = data["DailyReturn"].iloc[-1]

    market_cap_value.config(
        text=(
            "$" + format_number(market_cap)
            if market_cap
            else "N/A"
        )
    )

    pe_value.config(
        text=(
            f"{pe:.2f}"
            if pe
            else "N/A"
        )
    )

    avg_volume_value.config(
        text=format_number(avg_volume)
    )

    return_value.config(
        text=(
            f"{'+' if latest_return >= 0 else ''}"
            f"{latest_return:.2f}%"
        ),
        fg=GREEN if latest_return >= 0 else RED
    )

    # Trend

    sma20 = latest["SMA20"]
    sma50 = latest["SMA50"]

    if pd.notna(sma20) and pd.notna(sma50):

        if latest["Close"] > sma20 > sma50:

            trend = "BULLISH"
            trend_color = GREEN

            description = (
                "Price is above both moving averages "
                "and short-term momentum is positive."
            )

        elif latest["Close"] < sma20 < sma50:

            trend = "BEARISH"
            trend_color = RED

            description = (
                "Price is below both moving averages "
                "and short-term momentum is negative."
            )

        else:

            trend = "NEUTRAL"
            trend_color = YELLOW

            description = (
                "Price action is mixed and does not "
                "show a strong directional signal."
            )

    else:

        trend = "NEUTRAL"
        trend_color = YELLOW

        description = (
            "Not enough data to calculate the trend."
        )

    trend_label.config(
        text=f"● {trend.title()}",
        fg=trend_color
    )

    signal_value.config(
        text=trend,
        fg=trend_color
    )

    signal_description.config(
        text=description
    )

    # Main price chart

    ax.clear()

    dates = data["Date"]

    ax.plot(
        dates,
        data["Close"],
        color=ACCENT,
        linewidth=2,
        label="Price"
    )

    ax.plot(
        dates,
        data["SMA20"],
        color=GREEN,
        linewidth=1,
        alpha=0.8,
        label="SMA 20"
    )

    ax.plot(
        dates,
        data["SMA50"],
        color=YELLOW,
        linewidth=1,
        alpha=0.8,
        label="SMA 50"
    )

    ax.fill_between(
        range(len(data)),
        data["Close"].values,
        data["Close"].min(),
        color=ACCENT,
        alpha=0.04
    )

    ax.set_xticks(
        range(
            0,
            len(data),
            max(1, len(data) // 8)
        )
    )

    ax.set_xticklabels(
        [
            str(dates.iloc[i])[:10]
            for i in range(
                0,
                len(data),
                max(1, len(data) // 8)
            )
        ],
        rotation=30,
        ha="right",
        color=MUTED,
        fontsize=7
    )

    ax.yaxis.set_major_formatter(
        FuncFormatter(
            lambda x, _: f"${x:,.0f}"
        )
    )

    style_axis(ax)

    ax.legend(
        facecolor=PANEL,
        edgecolor=BORDER,
        labelcolor=TEXT,
        fontsize=8,
        loc="upper left"
    )

    figure.tight_layout()

    canvas.draw()

    # Volume chart

    volume_ax.clear()

    volume_ax.bar(
        range(len(data)),
        data["Volume"],
        color=ACCENT,
        alpha=0.65,
        width=1
    )

    volume_ax.set_xlim(
        0,
        len(data)
    )

    volume_ax.yaxis.set_major_formatter(
        FuncFormatter(
            lambda x, _: format_number(x)
        )
    )

    style_axis(volume_ax)

    volume_fig.tight_layout(
        pad=1
    )

    volume_canvas.draw()

    # Return chart

    return_ax.clear()

    returns = data["DailyReturn"].fillna(0)

    return_ax.plot(
        range(len(data)),
        returns,
        color=ACCENT,
        linewidth=1.2
    )

    return_ax.axhline(
        0,
        color=MUTED,
        linewidth=0.7,
        alpha=0.5
    )

    return_ax.yaxis.set_major_formatter(
        FuncFormatter(
            lambda x, _: f"{x:.1f}%"
        )
    )

    style_axis(return_ax)

    return_fig.tight_layout(
        pad=1
    )

    return_canvas.draw()


# ---------------------------------------------------------
# Keyboard shortcut
# ---------------------------------------------------------

ticker_entry.bind(
    "<Return>",
    lambda event: load_dashboard()
)


# ---------------------------------------------------------
# Start
# ---------------------------------------------------------

load_dashboard()

root.mainloop()