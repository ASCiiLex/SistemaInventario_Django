from django.core.paginator import Paginator


class ListViewMixin:
    paginate_by = 20
    allowed_sort_fields = []
    default_ordering = "id"

    def get_query_param(self, request, key, default=None):
        return request.GET.get(key, default)

    def paginate_queryset(self, request, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.get_query_param(request, "page", 1)

        try:
            page_obj = paginator.page(page_number)
        except:
            page_obj = paginator.page(1)

        return page_obj

    def is_htmx(self, request):
        return request.headers.get("HX-Request") == "true"

    def apply_ordering(self, request, queryset):
        sort = self.get_query_param(request, "sort")
        direction = self.get_query_param(request, "dir", "asc")

        if sort not in self.allowed_sort_fields:
            sort = self.default_ordering

        if direction == "desc":
            sort = f"-{sort}"

        return queryset.order_by(sort)

    def get_ordering_context(self, request):
        return {
            "current_sort": self.get_query_param(request, "sort", ""),
            "current_dir": self.get_query_param(request, "dir", "asc"),
        }