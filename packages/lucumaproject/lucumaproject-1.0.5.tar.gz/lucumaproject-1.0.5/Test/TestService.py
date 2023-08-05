class TestService:

    def assert_tests(self,interface):

        tables = interface.tables

        if (len(tables) > 0):
            for table in tables:
                for test in table.tests:
                    test.assert_test()
