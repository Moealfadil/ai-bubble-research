import seaborn as sns


def set_theme() -> None:
    sns.set_theme(style="whitegrid", context="talk")


PALETTE = {
    "AI": "#1f77b4",  # blue
    "Non-AI": "#2ca02c",  # green
}


