#!/usr/bin/env python3
import os
import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt

def detect_column(df, keywords):
    """Return first column name matching any of the keywords (case-insensitive)."""
    for col in df.columns:
        for kw in keywords:
            if kw.lower() == col.lower():
                return col
    for col in df.columns:
        for kw in keywords:
            if kw.lower() in col.lower():
                return col
    return None

def analyze_stats_file(path):
    df = pd.read_csv(path)

    # Verify 'Name' column
    if 'Name' not in df.columns:
        return None

    # Drop summary rows and keep only HTTP endpoints
    df = df[~df['Name'].isin(['Total', 'Aggregated'])]
    df = df[df['Name'].str.startswith('/')]
    df['endpoint'] = df['Name'].str.split('?').str[0]

    # Filter /data endpoint
    data_rows = df[df['endpoint'] == '/data']
    if data_rows.empty:
        return None

    # Detect relevant columns
    avg_rt_col   = detect_column(data_rows, ['Average Response Time', 'Average response time'])
    rps_col      = detect_column(data_rows, ['Requests/s', 'RPS'])
    failures_col = detect_column(data_rows, ['Failures'])

    if not avg_rt_col:
        return None

    # Compute simple average response time
    simple_avg = data_rows[avg_rt_col].mean()

    # Sum throughput and failures
    throughput = round(data_rows[rps_col].sum(), 2) if rps_col else None
    failures   = int(data_rows[failures_col].sum()) if failures_col else 0

    scenario = os.path.basename(path).replace('_stats.csv', '')

    return {
        'scenario': scenario,
        'avg_response_time': round(simple_avg, 2),
        'requests_per_s': throughput,
        'failures': failures
    }

def load_results():
    stats_files = glob.glob('tests/results/*_stats.csv')
    results = []
    for path in stats_files:
        res = analyze_stats_file(path)
        if res:
            results.append(res)
    if not results:
        print("⚠️  No valid data to plot.")
        sys.exit(1)
    return pd.DataFrame(sorted(results, key=lambda x: x['scenario']))

def plot_bar(x, y, ylabel, title, outpath):
    plt.figure()
    plt.bar(x, y)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath)
    print(f"✅ Saved {title}: {outpath}")

def main():
    df = load_results()

    # Ensure output directories
    os.makedirs('tests/reports/graphs', exist_ok=True)
    os.makedirs('tests/reports', exist_ok=True)

    # 1) All scenarios
    plot_bar(
        df['scenario'], df['avg_response_time'],
        'Avg Response Time (ms)',
        'Average Response Time by Scenario',
        'tests/reports/graphs/avg_response_time.png'
    )
    plot_bar(
        df['scenario'], df['requests_per_s'],
        'Requests per Second',
        'Throughput by Scenario',
        'tests/reports/graphs/throughput.png'
    )

    # 2) Compare MISS: 1 vs 3 Gateways (Cache MISS)
    miss = df[df['scenario'].isin(['results_1_gateway_miss', 'results_3_gateways_miss'])]
    plot_bar(
        miss['scenario'], miss['avg_response_time'],
        'Avg Response Time (ms)',
        'Response Time: 1 vs 3 Gateways (Cache MISS)',
        'tests/reports/graphs/rt_1v3_miss.png'
    )
    plot_bar(
        miss['scenario'], miss['requests_per_s'],
        'Requests per Second',
        'Throughput: 1 vs 3 Gateways (Cache MISS)',
        'tests/reports/graphs/th_1v3_miss.png'
    )

    # 3) Compare HIT vs MISS: 3 Gateways
    cmp = df[df['scenario'].isin(['results_3_gateways_hit', 'results_3_gateways_miss'])]
    plot_bar(
        cmp['scenario'], cmp['avg_response_time'],
        'Avg Response Time (ms)',
        'Response Time: 3 Gateways HIT vs MISS',
        'tests/reports/graphs/rt_3_hit_vs_miss.png'
    )
    plot_bar(
        cmp['scenario'], cmp['requests_per_s'],
        'Requests per Second',
        'Throughput: 3 Gateways HIT vs MISS',
        'tests/reports/graphs/th_3_hit_vs_miss.png'
    )

    # Generate summary Markdown
    summary_lines = [
        "# Benchmark Summary",
        "",
        "| Scenario | Avg Response Time (ms) | Requests/s | Failures |",
        "|----------|------------------------|------------|----------|"
    ]
    for _, r in df.iterrows():
        summary_lines.append(
            f"| {r.scenario} | {r.avg_response_time} | {r.requests_per_s} | {r.failures} |"
        )
    summary_path = 'tests/reports/summary.md'
    with open(summary_path, 'w') as f:
        f.write("\n".join(summary_lines))
    print(f"✅ Saved summary markdown: {summary_path}")

if __name__ == '__main__':
    main()
