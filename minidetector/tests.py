import os.path
from unittest import TestSuite, TestCase, TextTestRunner, TestLoader

from middleware import MiniDetectorMiddleware



class DummyRequest(object):
    def __init__(self, useragent):
        self.META = {'HTTP_USER_AGENT': useragent}

class TestHTTPHeaders(TestCase):
    """Everything that Isn't a User-Agent Header"""
    
    
    def test_wap(self):
        request = DummyRequest("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8b5) Gecko/20051019 Flock/0.4 Firefox/1.0+")
        request.META['HTTP_ACCEPT'] = 'application/vnd.wap.xhtml+xml, application/xhtml+xml, text/html, image/jpg, image/jpeg, image/png'        
        MiniDetectorMiddleware.process_request(request)
        self.assertTrue(request.is_wap, "WAP not Detected")
        
        request.META['HTTP_ACCEPT'] = 'application/xhtml+xml, text/html, application/vnd.wap.xhtml+xml, image/jpg, image/jpeg, image/png'        
        MiniDetectorMiddleware.process_request(request)
        self.assertFalse(request.is_wap, "WAP Detected")
        
        request.META['HTTP_ACCEPT'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        MiniDetectorMiddleware.process_request(request)
        self.assertFalse(request.is_wap, "WAP Detected")        
                
        
    def test_opera_mini(self):
        request = DummyRequest("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8b5) Gecko/20051019 Flock/0.4 Firefox/1.0+")
        request.META['HTTP_X_OPERAMINI_FEATURES'] = 'secure'
        MiniDetectorMiddleware.process_request(request)
        self.assert_(request.is_mobile, "Opera Mini not Detected")


def MobileDetectionFactory(uas, expected):
    class MobileDetection(TestCase):

        def testUA(self, ua):
            request = DummyRequest(ua)
            MiniDetectorMiddleware.process_request(request)
            if self.expected:
                self.assert_(request.is_mobile,
                             "Mobile Not Detected: %s" % ua)
            else:
                self.assert_(not request.is_mobile,
                             "Mobile Falsely Detected: %s" % ua)
    def testnum(num):
        def test(self):
            return self.testUA(self.uas[num])
        return test
    MobileDetection.uas = uas
    MobileDetection.expected = expected
    suite = TestSuite()
    for x in range(len(uas)):
        if not uas[x].startswith('#'):
            setattr(MobileDetection, 'test%s'%x, testnum(x))
            suite.addTest(MobileDetection('test%s' % x))
    return suite


def suite_from_file(filename, expected):
    f = None
    try:
        f = open(os.path.join(os.path.dirname(__file__), filename))
        uas = f.readlines()
    finally:
        if f:
            f.close()

    suite = MobileDetectionFactory(uas=uas, expected=expected)
    return suite


def gen_suite():
    suite = TestSuite()
    suite.addTest(suite_from_file('test_strings/mobile_useragents.txt', True))
    suite.addTest(suite_from_file('test_strings/other_useragents.txt', False))
    suite.addTests(TestLoader().loadTestsFromTestCase(TestHTTPHeaders))
    return suite

suite = gen_suite()

if __name__ == "__main__":
    TextTestRunner().run(suite)
