import unittest

from backup_manager.db.sqlite_helper import *
from backup_manager.backup.plans import *


class TestPlansMethods(unittest.TestCase):

    def reset(self):
        try:
            sql = get_sql_connection()
            drop_plans_table(sql)
            create_table_plans_if_not_exists(sql)
        except sqlite3.Error:
            self.fail("could not start connection with db and create table if not exists")

        plans = []
        return sql, plans

    def setUp(self):
        self.reset()

    def test_add_plan(self):
        def test(title, description, src, dest, mode, batch, expected_status):

            sql, plans = self.reset()

            if expected_status:
                add_plan(sql, plans, title, description, src, dest, mode, batch)
            else:
                with self.assertRaises(ValueError):
                    add_plan(sql, plans, title, description, src, dest, mode, batch)

            try:
                new_plans = get_plans_from_db(sql)
            except sqlite3.Error:
                self.fail("could not get plans from db")

            try:
                expected_plan = {TITLE: title,
                                 DESCRIPTION: description,
                                 SRC: src,
                                 DEST: dest,
                                 MODE: int(mode),
                                 BATCH: batch}
            except ValueError:
                expected_plan = {}

            self.assertListEqual(new_plans, plans)
            if len(plans) > 0:
                self.assertDictEqual(new_plans[0], expected_plan)
                self.assertDictEqual(plans[0], plans[0])

            try:
                close(sql)
            except sqlite3.Error:
                self.fail()

        test("1title", "2description", "3src", "4dest", "1", "5batch", True)
        test("_____", "_____\"\"!", "%%:myC:", "%//%J:", "2", "aweirdbatch2", True)
        test("1title", "2description", "3src", "4dest", "3", "5batch", False)
        test("1title", "2description", "3src", "4dest", "c", "5batch", False)




if __name__ == '__main__':
    unittest.main()
