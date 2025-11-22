import seaborn as sns


def set_theme() -> None:
    sns.set_theme(style="whitegrid", context="talk")


PALETTE = {
    "Pure-Play AI": "#d62728",  # red
    "AI-Exposed / Big Tech": "#1f77b4",  # blue
    "Non-AI / Control Group": "#2ca02c",  # green
}


