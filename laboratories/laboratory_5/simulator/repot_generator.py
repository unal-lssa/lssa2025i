import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime


def generate_status_report_pdf(json_path, pdf_dir="."):
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"status_report_{timestamp}.pdf"
    pdf_path = f"{pdf_dir}/{pdf_filename}"

    # Load data
    with open(json_path, "r") as f:
        data = json.load(f)

    # Initialize PDF
    with PdfPages(pdf_path) as pdf:
        # 1. Total requests per service graph
        total_requests = {
            service: sum(map(int, codes.values()))
            for service, codes in data.items()
        }

        plt.figure(figsize=(8, 6))
        plt.bar(total_requests.keys(), total_requests.values(), color='skyblue')
        plt.title("Total Requests per Service")
        plt.ylabel("Number of Requests")
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # 2. Status codes per service graph
        for service, codes in data.items():
            plt.figure(figsize=(6, 4))
            codes_sorted = dict(sorted(codes.items()))
            codes_list = list(codes_sorted.keys())
            counts = [int(v) for v in codes_sorted.values()]

            # Asignar color rojo si no está en el rango 200–299
            colors = [
                'lightgreen' if 200 <= int(code) < 300 else 'red'
                for code in codes_list
            ]

            plt.bar(codes_list, counts, color=colors)
            plt.title(f"Status Codes in {service}")
            plt.xlabel("HTTP Code")
            plt.ylabel("Count")
            plt.tight_layout()
            pdf.savefig()
            plt.close()

        # 3. Textual report (two columns)
        report_text = []
        report_text.append("Status Report Summary:\n")

        for service, codes in data.items():
            total_requests_service = sum(map(int, codes.values()))
            report_text.append(f"\nService: {service}")
            report_text.append(f"Total Requests: {total_requests_service}")
            for code, count in codes.items():
                report_text.append(f"  Code {code}: {count} requests")

        # Add the report in two columns
        fig, ax = plt.subplots(figsize=(8, 11))
        ax.axis('off')

        # Split the text into two roughly equal parts
        midpoint = len(report_text) // 2
        left_text = "\n".join(report_text[:midpoint])
        right_text = "\n".join(report_text[midpoint:])

        # Place the two columns of text
        ax.text(0.05, 0.95, left_text, fontsize=10, ha='left', va='top', wrap=True)
        ax.text(0.55, 0.95, right_text, fontsize=10, ha='left', va='top', wrap=True)

        pdf.savefig()
        plt.close()

    print(f"PDF report generated at: {pdf_path}")
