from rest_framework.throttling import SimpleRateThrottle


class OtpRequestThrottle(SimpleRateThrottle):
    scope = 'otp_request'

    def get_cache_key(self, request, view):
        email = request.data.get('email') 
        if email:
            ident = email.lower()

        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {'scope': self.scope, 'ident': ident}

class OtpVerifyThrottle(SimpleRateThrottle):
    scope = 'otp_verify'

    def get_cache_key(self, request, view):
        email = request.data.get('email') 
        if email:
            ident = email.lower()

        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {'scope': self.scope, 'ident': ident}


