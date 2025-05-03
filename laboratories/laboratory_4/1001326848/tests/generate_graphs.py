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

    # Verificar columna 'Name'
    if 'Name' not in df.columns:
        print(f"⚠️  File {path} has no 'Name' column, skipping.")
        return None

    # Eliminar filas de resumen y conservar solo endpoints HTTP
    df = df[~df['Name'].isin(['Total', 'Aggregated'])]
    df = df[df['Name'].str.startswith('/')]

    if df.empty:
        print(f"⚠️  No endpoint entries in {path}, skipping.")
        return None

    # Quitar query strings para agrupar por endpoint
    df['endpoint'] = df['Name'].str.split('?').str[0]

    # Filtrar solo /data
    data_rows = df[df['endpoint'] == '/data']
    if data_rows.empty:
        print(f"⚠️  No '/data' entries in {path}, skipping.")
        return None

    # Detectar columnas relevantes
    avg_rt_col   = detect_column(data_rows, ['Average Response Time', 'Average response time'])
    rps_col      = detect_column(data_rows, ['Requests/s', 'RPS'])
    failures_col = detect_column(data_rows, ['Failures'])

    if not avg_rt_col:
        print(f"⚠️  Avg Response Time column not found in {path}, skipping.")
        return None

    # Cálculo de promedio simple
    simple_avg = data_rows[avg_rt_col].mean()

    # Sumar throughput y fallas
    throughput = round(data_rows[rps_col].sum(), 2) if rps_col else None
    failures   = int(data_rows[failures_col].sum()) if failures_col else 0

    scenario = os.path.basename(path).replace('_stats.csv', '')

    return {
        'scenario': scenario,
        'avg_response_time': round(simple_avg, 2),
        'requests_per_s': throughput,
        'failures': failures
    }

def main():
    stats_files = glob.glob('tests/results/*_stats.csv')
    if not stats_files:
        print("⚠️  No stats CSV files found in tests/results/.")
        sys.exit(1)

    results = []
    for path in stats_files:
        res = analyze_stats_file(path)
        if res:
            results.append(res)

    if not results:
        print("⚠️  No valid data to plot.")
        sys.exit(1)

    # Ordenar y crear DataFrame
    results = sorted(results, key=lambda x: x['scenario'])
    df = pd.DataFrame(results)

    # Crear carpetas de salida
    os.makedirs('tests/reports/graphs', exist_ok=True)
    os.makedirs('tests/reports', exist_ok=True)

    # Gráfica: Tiempo de respuesta promedio
    plt.figure()
    plt.bar(df['scenario'], df['avg_response_time'])
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Avg Response Time (ms)')
    plt.title('Average Response Time by Scenario')
    plt.tight_layout()
    avg_chart = 'tests/reports/graphs/avg_response_time.png'
    plt.savefig(avg_chart)
    print(f"✅ Saved avg response time chart: {avg_chart}")

    # Gráfica: Throughput
    plt.figure()
    plt.bar(df['scenario'], df['requests_per_s'])
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Requests per Second')
    plt.title('Throughput by Scenario')
    plt.tight_layout()
    thr_chart = 'tests/reports/graphs/throughput.png'
    plt.savefig(thr_chart)
    print(f"✅ Saved throughput chart: {thr_chart}")

    # Generar resumen Markdown
    summary_lines = [
        "# Benchmark Summary",
        "",
        "| Scenario | Avg Response Time (ms) | Requests/s | Failures |",
        "|----------|------------------------|------------|----------|"
    ]
    for r in results:
        summary_lines.append(
            f"| {r['scenario']} | {r['avg_response_time']} | {r['requests_per_s']} | {r['failures']} |"
        )

    summary_path = 'tests/reports/summary.md'
    with open(summary_path, 'w') as f:
        f.write("\n".join(summary_lines))
    print(f"✅ Saved summary markdown: {summary_path}")

if __name__ == '__main__':
    main()
