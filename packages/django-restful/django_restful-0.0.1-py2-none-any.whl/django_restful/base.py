# -*- coding: utf-8 -*-

from rest_framework.views import APIView


class RestfulApiView(APIView):

    def dispatch(self, request, *args, **kwargs):
        """
        通过在url中配置MIME_TYPE路由到view中的处理程序，在没有配置的情况下默认路由到http_method_name对应的处理程序，
        在配置的情况下路由到MIME_TYPE对应的处理程序，同时要判断该处理程序的http_method_name.
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # 在url中配置用于路由到view中的处理方法
            mime_type = kwargs.get('MIME_TYPE', None)

            http_method_name = request.method.lower()

            if http_method_name in self.http_method_names:
                if mime_type is not None:
                    handler = getattr(
                        self, mime_type, self.http_method_not_allowed)

                    handler_method_names = getattr(
                        handler, 'http_method_names', None)
                    if http_method_name not in handler_method_names:
                        handler = self.http_method_not_allowed

                    del self.kwargs['MIME_TYPE']
                else:
                    handler = getattr(self, http_method_name,
                                      self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(
            request, response, *args, **kwargs)
        return self.response
