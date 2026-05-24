import os
import shutil
import subprocess
import sys
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


def get_report_root(feature_paths):
    joined_paths = " ".join(feature_paths).lower().replace("/", "\\")

    if "features\\e2e" in joined_paths:
        return os.path.join("reports", "e2e")

    if "features\\testcases" in joined_paths:
        return os.path.join("reports", "testcases")

    return os.path.join("reports", "combined")


def clean_old_reports(report_root):
    folders = (
        os.path.join(report_root, "allure-results"),
        os.path.join(report_root, "allure-report"),
        os.path.join(report_root, "screenshots"),
    )

    for folder in folders:
        if os.path.exists(folder):
            logger.info("Deleting old folder: %s", folder)
            shutil.rmtree(folder)

        os.makedirs(folder, exist_ok=True)


def run_behave():
    feature_paths = sys.argv[1:] if len(sys.argv) > 1 else ["features"]
    report_root = get_report_root(feature_paths)
    allure_results = os.path.join(report_root, "allure-results")
    allure_report = os.path.join(report_root, "allure-report")
    screenshots = os.path.join(report_root, "screenshots")

    clean_old_reports(report_root)
    os.environ["SCREENSHOTS_PATH"] = screenshots

    logger.info("Automation execution started: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Feature path: %s", ", ".join(feature_paths))
    logger.info("Report root: %s", report_root)

    cmd = [
        sys.executable,
        "-m",
        "behave",
        "-f",
        "allure_behave.formatter:AllureFormatter",
        "-o",
        allure_results,
        "-f",
        "pretty",
        "-o",
        "pretty.output",
    ]

    cmd.extend(feature_paths)

    result = subprocess.run(cmd, check=False)

    logger.info("Automation execution finished with code: %s", result.returncode)

    allure_cmd = shutil.which("allure.bat") or shutil.which("allure")

    if allure_cmd:
        subprocess.run(
            [allure_cmd, "generate", allure_results, "-o", allure_report, "--clean"],
            check=False,
            shell=allure_cmd.lower().endswith(".bat"),
        )
    else:
        logger.warning("Allure commandline is not installed. Results are still saved in %s.", allure_results)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(run_behave())