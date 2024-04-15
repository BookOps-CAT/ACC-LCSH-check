from acc_lcsh_check.log import LogSession

if __name__ == "__main__":
    logger = LogSession(
        logger_name="monthly_lcsh_check",
        logfile="lcsh.log",
        infile="data/test_file.csv",
        outfile="data/acc_out.csv",
    )
    logger.run_logger()
    logger.rename_files()
