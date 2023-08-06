import unittest
import sys
import os


# Hopefully I can import the planner package another way...
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import termplanner.planner as planner


class PlannerTestCase(unittest.TestCase):
    def setUp(self):
        """Sets up a temporary planner and database"""
        self.temp_planner = planner.Planner(db_name="tempdb.db")
        self.temp_planner.make_db()

    def tearDown(self):
        """Destroys the database."""
        self.temp_planner.close_connection()
        os.remove(self.temp_planner.db)

    def test_create_event(self):
        """Ensure that create_event function properly inserts event
        and date values into their correspondent columns.
        """
        self.temp_planner.create_event("5.7.2000", "My birth")

    def test_read_all(self):
        """Test whether the planner object can properly read through the db."""
        self.temp_planner.read_all()

    def test_checkout(self):
        """Test the checkout function."""
        self.temp_planner.checkout("My birth", False)


if __name__ == '__main__':
    unittest.main()
