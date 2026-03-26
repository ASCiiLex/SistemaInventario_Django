from django.core.paginator import Paginator


class ListViewMixin:
    paginate_by = 25

    def paginate_queryset(self, request, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def is_htmx(self, request):
        return request.headers.get("HX-Request")