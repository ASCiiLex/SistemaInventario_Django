from django.core.paginator import Paginator


class ListViewMixin:
    paginate_by = 20
    default_ordering = None
    allowed_sort_fields = []

    def paginate_queryset(self, request, queryset):
        paginator = Paginator(queryset, self.paginate_by)

        page_number = request.GET.get("page", 1)

        try:
            page_obj = paginator.page(page_number)
        except:
            page_obj = paginator.page(1)

        return page_obj

    def is_htmx(self, request):
        return request.headers.get("HX-Request") == "true"

    # 🔥 NUEVO: ORDENACIÓN UNIVERSAL
    def apply_ordering(self, request, queryset):
        sort = request.GET.get("sort")
        direction = request.GET.get("dir", "asc")

        if sort and sort in self.allowed_sort_fields:
            if direction == "desc":
                sort = f"-{sort}"
            queryset = queryset.order_by(sort)
        elif self.default_ordering:
            queryset = queryset.order_by(self.default_ordering)

        return queryset