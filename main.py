import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import io
import tempfile

def is_column_plottable(series, total_rows):
    if series.nunique() >= total_rows * 0.7:
        return False
    if series.nunique() <= 1:
        return False
    return True

def auto_visualize(csv_file):
    try:
        df = pd.read_csv(csv_file.name)
    except Exception as e:
        return [], f"❌ Error reading file: {str(e)}"

    total_rows = len(df)
    plots = []

    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = df.select_dtypes(exclude='number').columns

    # Generate numeric plots
    for col in numeric_cols:
        if is_column_plottable(df[col], total_rows):
            fig, ax = plt.subplots()
            df[col].plot(ax=ax, title=f"Line Plot of {col}")
            ax.set_ylabel(col)
            plt.tight_layout()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                plt.savefig(tmpfile.name)
                plots.append(tmpfile.name)
            plt.close(fig)

    # Generate categorical plots
    for col in categorical_cols:
        if is_column_plottable(df[col], total_rows) and df[col].nunique() < 20:
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind='bar', ax=ax, title=f"Bar Chart of {col}")
            plt.tight_layout()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                plt.savefig(tmpfile.name)
                plots.append(tmpfile.name)
            plt.close(fig)

    # Fallback: show summary if no plots were created
    if not plots:
        summary = "<h3>📋 Data Summary</h3>"
        summary += df.describe(include='all').to_html()
        summary += "<br><br><strong>Columns:</strong><br>" + "<br>".join(df.columns)
        return [], summary

    return plots, ""  # Plots exist, no need to show summary

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📊 CSV Auto-Visualization Dashboard")

    with gr.Row():
        file_input = gr.File(label="Upload CSV", file_types=[".csv"])

    with gr.Row():
        output_area = gr.Gallery(label="📈 Auto Charts", columns=2)
        summary_box = gr.HTML(label="ℹ️ Summary (if no charts)")

    file_input.change(fn=auto_visualize, inputs=file_input, outputs=[output_area, summary_box])

demo.launch(mcp_server=True)
