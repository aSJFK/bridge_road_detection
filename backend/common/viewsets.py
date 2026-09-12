"""统一 ViewSet：让所有 CRUD 响应保持 {code, data, message} 格式"""

from rest_framework import status, viewsets
from rest_framework.response import Response

from .responses import ok, fail


class ApiModelViewSet(viewsets.ModelViewSet):
    """统一响应格式的 ModelViewSet"""

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 200,
                    "data": {
                        "count": self.paginator.page.paginator.count,
                        "page": self.paginator.page.number,
                        "page_size": self.paginator.page_size,
                        "results": serializer.data,
                    },
                    "message": "success",
                }
            )
        serializer = self.get_serializer(queryset, many=True)
        return ok(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ok(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ok(
            data=serializer.data,
            message="创建成功",
            code=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ok(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ok(data=None, message="删除成功")


class ApiReadOnlyModelViewSet(ApiModelViewSet, viewsets.ReadOnlyModelViewSet):
    """统一响应格式的只读 ViewSet"""

    def create(self, *args, **kwargs):  # pragma: no cover
        return fail("只读接口", 405)

    def update(self, *args, **kwargs):  # pragma: no cover
        return fail("只读接口", 405)

    def destroy(self, *args, **kwargs):  # pragma: no cover
        return fail("只读接口", 405)
