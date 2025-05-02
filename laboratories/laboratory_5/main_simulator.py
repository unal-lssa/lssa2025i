from simulator.simulator import main
from simulator.repot_generator import generate_status_report_pdf

if __name__ == "__main__":
    main()
    generate_status_report_pdf("simulator/status_log.json")