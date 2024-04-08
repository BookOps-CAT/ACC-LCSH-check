import datetime

from acc_lcsh_check.log import LogSession

if __name__ == "__main__":
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    logger = LogSession(
        logger_name="monthly_lcsh_check",
        logfile="data/lcsh.log",
        infile="data/acc_in.csv",
        outfile="data/acc_out.csv",
    )
    logger.run_logger()
    logger.rename_files()
