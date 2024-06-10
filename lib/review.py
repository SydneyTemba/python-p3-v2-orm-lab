from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee ID: {self.employee_id}>"

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and summary:
            self._summary = summary
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if isinstance(employee_id, int) and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError("Employee ID must reference an employee in the database")

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review instance.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
        """

        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review object having the attribute values from the table row."""

        # Check the dictionary for an existing instance using the row's primary key
        review = cls.all.get(row[0])
        if review:
            # ensure attributes match row values in case local instance was modified
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            # not in dictionary, create new instance and add to dictionary
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review
        return review

   