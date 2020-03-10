import re
import codecs
import logging
from sys import exit
from argparse import ArgumentParser
from gzip import open as gzipopen
from ast import literal_eval
from datetime import datetime
from os import listdir, path
from collections import namedtuple, defaultdict
from statistics import median
from string import Template

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

parser = ArgumentParser()
parser.add_argument('--config', type=open, default='./config.txt', help='Dir of config')
args = parser.parse_args()

real_args = literal_eval(args.config.read())
for key in config.keys():
    if key not in real_args.keys():
        real_args[key] = config[key]


log_format = '[%(asctime)s] %(levelname).1s %(message)s'
logging.basicConfig(level=logging.DEBUG,
                    filename=path.join(real_args['LOG_DIR'], 'myapp.log'),
                    format=log_format,
                    datefmt='%Y.%m.%d %H:%M:%S')


def find_most_actual(log_dir):
    logging.info(f'starting look for most actual log file in {log_dir}')
    file_pattern = r'nginx-access-ui.log-(.+?)(.gz|.txt)'
    list_of_logs = (i for i in listdir(log_dir) if re.match(file_pattern, i))
    file_most_actual = max(list_of_logs)
    date_most_actual = re.search(file_pattern, file_most_actual).group(1)
    date_most_actual = datetime.strptime(date_most_actual, "%Y%m%d").date().strftime("%Y.%m.%d")
    extension = re.search(file_pattern, file_most_actual).group(2)
    file = namedtuple('file', ['name', 'date', 'extention'])
    file_most_actual = path.join(log_dir, file_most_actual)
    file.name = file_most_actual
    file.date = date_most_actual
    file.extension = extension
    logging.info(f"most actual log file is {file_most_actual}")
    return file


def extract_info(log_string):
    log_string = str(log_string, 'utf-8')
    url, time_delta = log_string.split(' ')[7], log_string.split(' ')[-1]
    time_delta = float(time_delta)
    return url, time_delta


def xreadlines(log_path):
    logging.info('starting processing lines')
    if log_path.endswith(".gz"):
        logs = gzipopen(log_path, 'rb')
    else:
        logs = open(log_path)
    global_time_sum = global_cnt_sum = 0
    total = 0
    for log in logs:
        total += 1
        try:
            url, time_delta = extract_info(log)
            global_cnt_sum += 1
            global_time_sum += time_delta
            yield url, time_delta
        except:
            pass
    logs.close()
    if total != 0:
        calc_share = global_cnt_sum/total*100
    else:
        calc_share = 1
    if calc_share < 50:
        raise Exception(f'The value of unprocessed lines is{calc_share}')
    else:
        logging.info('lines are succesfully procesed')


def form_table_for_template(name, report_size):
    logging.info('starting collect summary')

    file_processed = defaultdict(list)
    mg = xreadlines(name)

    global_time_sum = 0
    global_cnt_sum = 0
    for url, time_delta in mg:
        global_time_sum += time_delta
        global_cnt_sum += 1
        file_processed[url].append(time_delta)

    metrics = []
    for url, time_delta in file_processed.items():
        metrics.append({"count": len(time_delta), "time_avg": sum(time_delta) / len(time_delta),
                        "time_max": max(time_delta), "time_sum": sum(time_delta),
                        "url": url, "time_med": median(time_delta),
                        "time_perc": sum(time_delta) / global_time_sum,
                        "count_perc": len(time_delta) / global_cnt_sum})

    metrics = sorted(metrics, key=lambda i: i['time_sum'], reverse=True)[0:report_size]
    logging.info('summary collected')
    return metrics


def load_html(file_most_actual, metrics, report_dir):
    logging.info('starting creating html')
    html_template = Template(codecs.open("report.html", 'r').read())
    html_save = html_template.safe_substitute(table_json=str(metrics))
    table_sorter_addr = "./jquery.tablesorter.min.js"
    html_save = html_save.replace("jquery.tablesorter.min.js", table_sorter_addr)
    date_most_actual = file_most_actual.date
    filename = f'report-{date_most_actual}.html'
    html_file = open(path.join(report_dir, filename), "w")
    html_file.write(html_save)
    html_file.close()
    logging.info(f'html in {path.join(report_dir,filename)} succesfuly created')


def main(log_dir, report_dir, report_size):
    try:
        file_actual = find_most_actual(log_dir)
        html_pattern = r'report-(.+?).html'

        list_of_html = [i for i in listdir(report_dir) if re.match(html_pattern, i)]
        if list_of_html:
            last_html = max(list_of_html)
            html_date_most_actual = re.search(html_pattern, last_html).group(1)
        else:
            html_date_most_actual = 0
        if file_actual.date == html_date_most_actual:
            logging.info('Most actual log have been processed before')
            exit()
        else:
            pass

    except Exception as e:
        exception_message = "Error in looking for most actual log"
        logging.exception(exception_message)
        logging.error(e)

    try:
        metrics = form_table_for_template(file_actual.name, report_size)

    except Exception as e:
        exception_message = "Error in looking for most actual log"
        logging.exception(exception_message)
        logging.error(e)

    try:
        load_html(file_actual, metrics, report_dir)

    except Exception as e:
        exception_message = "Error in loading html"
        logging.exception(exception_message)
        logging.error(e)


if __name__ == "__main__":
    main(real_args['LOG_DIR'], real_args['REPORT_DIR'], real_args['REPORT_SIZE'])
