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

        # 🔥 fallback seguro
        if sort not in self.allowed_sort_fields:
            sort = self.default_ordering

        # 🔥 NATURAL SORT SOLO PARA product__name (sin romper DB)
        if sort == "product__name":
            queryset = sorted(
                queryset,
                key=lambda x: self._natural_key(x.product.name)
            )
            if direction == "desc":
                queryset = list(reversed(queryset))
            return queryset

        if direction == "desc":
            sort = f"-{sort}"

        return queryset.order_by(sort)

    def _natural_key(self, text):
        import re
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', text)]

    def get_ordering_context(self, request):
        return {
            "current_sort": self.get_query_param(request, "sort", ""),
            "current_dir": self.get_query_param(request, "dir", "asc"),
        }