"""Plotly Visualizer 1.0.0.

Create interactive HTML visualizations from CSV data using Plotly Express.

by
    Urgap Team 2025

"""

import argparse

from pathlib import Path

import pandas as pd
import plotly.express as px


def create_plot(
    df: pd.DataFrame,
    plot_type: str,
    x_column: str | None,
    y_column: str | None,
    color_column: str | None,
    title: str | None,
) -> px.scatter:
    """Create a Plotly Express figure based on the specified plot type.

    Args:
        df: Input DataFrame.
        plot_type: Type of plot (scatter, bar, line, histogram, box, violin, heatmap).
        x_column: Column name for x-axis.
        y_column: Column name for y-axis.
        color_column: Optional column name for color grouping.
        title: Optional plot title.

    Returns:
        Plotly Express figure object.

    Raises:
        ValueError: If plot_type is not supported.
    """
    plot_kwargs = {
        "data_frame": df,
        "title": title,
    }

    if x_column:
        plot_kwargs["x"] = x_column
    if y_column:
        plot_kwargs["y"] = y_column
    if color_column:
        plot_kwargs["color"] = color_column

    plot_functions = {
        "scatter": px.scatter,
        "bar": px.bar,
        "line": px.line,
        "histogram": px.histogram,
        "box": px.box,
        "violin": px.violin,
        "heatmap": px.density_heatmap,
    }

    if plot_type not in plot_functions:
        msg = (
            f"Unsupported plot type: {plot_type}. "
            f"Supported types: {list(plot_functions.keys())}"
        )
        raise ValueError(msg)

    if plot_type == "histogram" and y_column is None:
        plot_kwargs.pop("y", None)

    return plot_functions[plot_type](**plot_kwargs)


def main(
    csv_file: str | Path,
    output_file: str | Path,
    plot_type: str = "scatter",
    x_column: str | None = None,
    y_column: str | None = None,
    color_column: str | None = None,
    title: str | None = None,
) -> None:
    """Create a Plotly visualization from CSV data and save as HTML.

    Args:
        csv_file: Path to input CSV file.
        output_file: Path for output HTML file.
        plot_type: Type of plot to create.
        x_column: Column name for x-axis.
        y_column: Column name for y-axis.
        color_column: Optional column name for color grouping.
        title: Optional plot title.
    """
    df = pd.read_csv(csv_file)

    fig = create_plot(
        df=df,
        plot_type=plot_type,
        x_column=x_column,
        y_column=y_column,
        color_column=color_column,
        title=title,
    )

    fig.write_html(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Plotly visualizations from CSV data.",
    )
    parser.add_argument(
        "--csv-file",
        required=True,
        help="Path to input CSV file.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path for output HTML file.",
    )
    parser.add_argument(
        "--plot-type",
        default="scatter",
        choices=["scatter", "bar", "line", "histogram", "box", "violin", "heatmap"],
        help="Type of plot to create.",
    )
    parser.add_argument(
        "--x-column",
        default=None,
        help="Column name for x-axis.",
    )
    parser.add_argument(
        "--y-column",
        default=None,
        help="Column name for y-axis.",
    )
    parser.add_argument(
        "--color-column",
        default=None,
        help="Column name for color grouping.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Plot title.",
    )

    args = parser.parse_args()

    main(
        csv_file=args.csv_file,
        output_file=args.output_file,
        plot_type=args.plot_type,
        x_column=args.x_column,
        y_column=args.y_column,
        color_column=args.color_column,
        title=args.title,
    )
