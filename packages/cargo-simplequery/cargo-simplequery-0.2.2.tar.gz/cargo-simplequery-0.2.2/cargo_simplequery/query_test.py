import unittest

import os
import psycopg2

from query import SelectQueryBuilder, InsertQueryBuilder, UpdateQueryBuilder, DeleteQueryBuilder


class TestQueryBuiding(unittest.TestCase):

    def test_simple_select_all(self):
        q = SelectQueryBuilder('users', ['*'])
        self.assertEqual(q.get_query().as_string(self._connection), 'SELECT * FROM "users"')

    def test_select_with_where_and_limit(self):
        q = SelectQueryBuilder('users', ['*'])
        q.where().like('email', '%@gmail.com')
        q.limit(50, 0)
        self.assertEqual(q.get_query().as_string(self._connection),
"""SELECT * FROM "users"
WHERE ("email" LIKE '%@gmail.com')
LIMIT 50 OFFSET 0""")

    def test_select_join(self):
        q = SelectQueryBuilder('users u', ['u.id', 'u.email', 'g.name'])
        q.left_join('groups_users gu').on_eq('u.id', 'gu.user_id')
        q.left_join('groups g').on_eq('g.id', 'gu.group_id')
        self.assertEqual(q.get_query().as_string(self._connection),
'''SELECT "u"."id", "u"."email", "g"."name" FROM "users" AS "u"
LEFT JOIN "groups_users" AS "gu" ON "u"."id" = "gu"."user_id"
LEFT JOIN "groups" AS "g" ON "g"."id" = "gu"."group_id"''')

    def test_simple_escaping(self):
        q = SelectQueryBuilder('users', ['*'])
        q.where().eq('email', 'test\'inject')
        self.assertEqual(q.get_query().as_string(self._connection),
"""SELECT * FROM "users"
WHERE ("email" = 'test''inject')""")

    def test_insert(self):
        q = InsertQueryBuilder('users', ['email', 'name'])
        q.add_column('active')
        self.assertEqual(q.get_query().as_string(self._connection), 'INSERT INTO "users" ("email", "name", "active") VALUES (%s, %s, %s)')

    def test_update(self):
        q = UpdateQueryBuilder('users', ['email', 'name'])
        q.add_column('active')
        self.assertEqual(q.get_query().as_string(self._connection),
"""UPDATE "users" SET "email" = %s, "name" = %s, "active" = %s""")

    def test_update_with_where(self):
        q = UpdateQueryBuilder('users', ['email', 'name'])
        q.add_column('active')
        q.where().eq('id', 1)
        q.limit(1)
        self.assertEqual(q.get_query().as_string(self._connection),
"""UPDATE "users" SET "email" = %s, "name" = %s, "active" = %s
WHERE ("id" = 1)
LIMIT 1""")

    def test_delete(self):
        q = DeleteQueryBuilder('users')
        q.where().eq('id', 1)
        self.assertEqual(q.get_query().as_string(self._connection),
                         """DELETE FROM "users" WHERE ("id" = 1)""")

    @classmethod
    def setUpClass(cls):
        cls._connection = psycopg2.connect(os.environ.get('TEST_DSN'))

    @classmethod
    def tearDownClass(cls):
        cls._connection.close()


if __name__ == '__main__':
    unittest.main()