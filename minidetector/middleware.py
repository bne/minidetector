import re
from useragents import search_strings

class MiniDetectorMiddleware(object):
    @staticmethod
    def process_request(request):
        """Adds some simple details about the user agent to the request object
        """
        
        if request.META.has_key("HTTP_ACCEPT"):
            # 'wap' mimetype occurs before '(x)html' in accept header
            # Some wap enabled devices (like early BlackBerrys) prefer html 
            # over wml    
            # regex from http://stackoverflow.com/questions/3843596/regular-expression-to-match-wap-not-preceeded-by-html
            prefers_wap_re = re.compile(r'^(?!(?:(?!wap).)*html).*?wap', re.I)
            
            if bool(prefers_wap_re.search(request.META["HTTP_ACCEPT"])):
                
                request.is_mobile = True
                request.is_wap = True
                request.is_simple_device = True
                
                return None
                
        request.is_wap = False
                        
        if request.META.has_key("HTTP_X_OPERAMINI_FEATURES"):
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            
            request.is_mobile = True
            request.is_simple_device = True
            
            return None
        
        if request.META.has_key("HTTP_USER_AGENT"):
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            
            s = request.META["HTTP_USER_AGENT"].lower()
            
            if 'applewebkit' in s:
                request.is_mobile = True
                request.is_webkit = True
            
            if 'ipad' in s:
                request.is_mobile = True
                request.is_ios_device = True
                request.is_touch_device = True
                request.is_wide_device = True
                
                return None
            
            if 'iphone' in s or 'ipod' in s:
                request.is_mobile = True
                request.is_ios_device = True
                request.is_touch_device = True
                request.is_wide_device = False
                
                return None
            
            if 'android' in s:
                request.is_mobile = True
                request.is_android_device = True
                request.is_touch_device = True
                request.is_wide_device = False # TODO add support for andriod tablets
                
                return None
            
            if 'webos' in s:
                request.is_mobile = True
                request.is_webos_device = True
                request.is_touch_device = True
                request.is_wide_device = False # TODO add support for webOS tablets
                
                return None
            
            if 'windows phone' in s:
                request.is_mobile = True
                request.is_windows_phone_device = True
                request.is_touch_device = True
                request.is_wide_device = False
                
                return None
            
            for ua in search_strings:
                if ua in s:
                    request.is_mobile = True
                    request.is_simple_device = True
                    return None
        
        # defaults (we assume this is a desktop)
        request.is_mobile = False                
        request.is_simple_device = False
        request.is_touch_device = False
        request.is_wide_device = True
        
        return None

def detect_mobile(view):
    """ View Decorator that adds a "mobile" attribute to the request which is
        True or False depending on whether the request should be considered
        to come from a small-screen device such as a phone or a PDA"""
    
    def detected(request, *args, **kwargs):
        Middleware.process_request(request)
        return view(request, *args, **kwargs)
    detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
    return detected

__all__ = ['Middleware', 'detect_mobile']
