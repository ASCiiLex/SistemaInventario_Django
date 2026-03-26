from django.core.paginator import Paginator


class ListViewMixin:
    paginate_by = 20

    def paginate_queryset(self, request, queryset):
        paginator = Paginator(queryset, self.paginate_by)

        page_number = request.GET.get("page", 1)

        # 🔥 CLAVE: reset automático si page inválida
        try:
            page_obj = paginator.page(page_number)
        except:
            page_obj = paginator.page(1)

        return page_obj

    def is_htmx(self, request):
        return request.headers.get("HX-Request") == "true"