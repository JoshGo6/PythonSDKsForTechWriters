import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def parse_log_line(log_line):
    log_dict = {}
    fields = log_line.split()
    time = fields[0] + " " + fields[1]
    level = fields[2]
    method = fields[3]
    path = fields[4]
    status = fields[5]
    log_dict["timestamp"] = time
    log_dict["level"] = level
    log_dict["method"] = method
    log_dict["path"] = path
    log_dict["status"] = status
    return log_dict

file_name="21.txt"
error_num = 0
error_summary = ""
error_file = "21.err.txt"
try:
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            line_dict = parse_log_line(line)
            logging.debug(line_dict["level"])
            if line_dict["level"] == "ERROR":
                error_num += 1
                error_message = f"[{line_dict["timestamp"]}] {line_dict["status"]} {line_dict["path"]} \n"
                error_summary = error_summary + error_message
                logging.debug(error_message.rstrip())
            logging.info(f"Processed {line_dict['level']} {line_dict['path']}")
except FileNotFoundError:
      logging.error(f"File {file_name} doesn't exist.")
with open(error_file, "w", encoding="UTF-8") as f:
    f.write(error_summary)
logging.warning(f"Printed {error_num} errors to {error_file}.")
print(error_summary)