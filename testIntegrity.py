import unittest
import Model
import View
import Controller

class HandlerFactoryTestCase(unittest.TestCase):
    #Test for Model Handler Factory

    def testHandler1(self):
        handler = Model.HandlerFactory()
        self.assertTrue(handler.http_factory('nginx'))

    def testHandler2(self):
        handler = Model.HandlerFactory()
        self.assertTrue(handler.http_factory('Apache'))

    def testHandler3(self):
        handler = Model.HandlerFactory()
        self.assertTrue(handler.http_factory('gws'))

    def testHandler4(self):
        handler = Model.HandlerFactory()
        self.assertTrue(handler.http_factory('IIS'))

    def testHandler5(self):
        handler = Model.HandlerFactory()
        self.assertTrue(handler.https_factory())

class ServerFactoryTestCase(unittest.TestCase):
    
    def testServer1(self):
        server = Model.Server()
        self.assertTrue(server.factory('HTTP', 80))


    def testServer2(self):
        server = Model.Server()
        self.assertTrue(server.factory('HTTPS', 443))

    def testServer3(self):
        server = Model.Server()
        self.assertTrue(server.factory('DNS', 53))


    def testServer4(self):
        server = Model.Server()
        self.assertTrue(server.factory('Easy', 443))

if __name__ == '__main__':
    unittest.main()
