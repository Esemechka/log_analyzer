import unittest
from log_analyzer import find_most_actual, form_table_for_template
class TestLogAnalyzer(unittest.TestCase):

    def test_find_most_actual(self):
        """
        Test that it doesnt look for bz2 file and what it look
        for most actual and extract correctly date
        """
        log_dir_test = './folder_for_actual_file_search_test/'
        result = find_most_actual(log_dir_test)
        self.assertEqual(result.date, '2020.03.09')

    def test_on_empty_file(self):
        """
        Test not failing on empty file
        """
        file_test = './folder_for_actual_file_search_test/nginx-access-ui.log-20200309.txt'
        try:
            form_table_for_template(file_test, 1000)
        except:
            self.fail("empty file havent been processed")



if __name__ == '__main__':
    unittest.main()