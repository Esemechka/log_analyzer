# log_analyzer

Command to run script:

python log_analyzer.py --config="./folder_for_test/config_test.txt"
 
Command to run test:

python test.py


Pipeline for processing logs from LOG_DIR folder, gathering stats
about urls, take top REPORT_SIZE of url cnt, 
and render it to html to REPORT_DIR folder. Default configs 
to run script are in "config.txt".

Pipeline consist of several functions:

find_most_actual - looking for most actual file with log

extract_info - parse line of log, extract url and session
 time
 
xreadlines - generator for processing lines and check 
percentage of unprocessed lines. It raise exception if 
processed less than half of lines

form_table_for_template - collect list of dicts to insert 
into html template

load_html - generate html with result 


