from django.views.generic import ListView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from django_tables2 import SingleTableView, RequestConfig
from django.views.generic import ListView

# Create your views here.
from .forms import ResourcePlanCreateForm, ResourcePlanEditForm

from .models import Resource, ResourcePlan, ResourcePlanItem
from .tables import ResourceTable, ResourcePlanTable, ResourcePlanItemTable

class ResourcePlanView(SingleTableView):
    model = ResourcePlanItem
    template_name = 'resources/res_plan.html'

@method_decorator(staff_member_required, name='dispatch')
class HomepageView(ListView):
    template_name = 'index.html'
    model = ResourcePlan
    queryset = ResourcePlan.objects.all()[:10]


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rp = ResourcePlan.objects.all()
        # total_sales = rp.aggregate(Sum('final_value'))['final_value__sum'] if rp.exists() else 0
        # paid_value = rp.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum']\
        #     if rp.filter(is_paid=True).exists() else 0
        # remaining = total_sales - paid_value
        # diviner = total_sales if total_sales > 0 else 1
        # paid_percent, remain_percent = round((paid_value/diviner)*100, 1), round((remaining/diviner)*100, 1)
        # total_sales = f'{total_sales} {CURRENCY}'
        # paid_value = f'{paid_value} {CURRENCY}'
        # remaining = f'{remaining} {CURRENCY}'
        rp = ResourcePlanTable(rp)
        RequestConfig(self.request).configure(rp)
        context.update(locals())
        return context


@staff_member_required
def auto_create_order_view(request):
    new_order = ResourcePlan.objects.create(
        title='Resource Plan 66',
        date=datetime.datetime.now()

    )
    new_order.title = f'ResourcePlan - {new_order.id}'
    new_order.save()
    return redirect(new_order.get_edit_url())

@method_decorator(staff_member_required, name='dispatch')
class ResourcePlanListView(ListView):
    template_name = 'list.html'
    model = ResourcePlan
    paginate_by = 50

    def get_queryset(self):
        qs = ResourcePlan.objects.all()
        if self.request.GET:
            qs = ResourcePlan.filter_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rp = ResourcePlanTable(self.object_list)
        RequestConfig(self.request).configure(rp)
        context.update(locals())
        return context


@staff_member_required
def ajax_calculate_results_view(request):
    rp = ResourcePlan.filter_data(request, ResourcePlan.objects.all())
    total_value, total_paid_value, remaining_value, data = 0, 0, 0, dict()
    if rp.exists():
        total_value = rp.aggregate(Sum('final_value'))['final_value__sum']
        total_paid_value = rp.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if\
            rp.filter(is_paid=True) else 0
        remaining_value = total_value - total_paid_value
    total_value, total_paid_value, remaining_value = f'{total_value} {CURRENCY}',\
                                                     f'{total_paid_value} {CURRENCY}', f'{remaining_value} {CURRENCY}'
    data['result'] = render_to_string(template_name='include/result_container.html',
                                      request=request,
                                      context=locals())
    return JsonResponse(data)


@method_decorator(staff_member_required, name='dispatch')
class CreateResourcePlanView(CreateView):
    template_name = 'form.html'
    form_class = ResourcePlanCreateForm
    model = ResourcePlan

    def get_success_url(self):
        self.new_object.refresh_from_db()
        return reverse('update_order', kwargs={'pk': self.new_object.id})

    def form_valid(self, form):
        object = form.save()
        object.refresh_from_db()
        self.new_object = object
        return super().form_valid(form)    

@method_decorator(staff_member_required, name='dispatch')
class ResourcePlanUpdateView(UpdateView):
    model = ResourcePlan
    template_name = 'order_update.html'
    form_class = ResourcePlanEditForm


    def get_success_url(self):
        return reverse('update_order', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.object
        qs_p = Resource.objects.filter(active=True)[:12]
        products = ResourceTable(qs_p)
        order_items = ResourcePlanItemTable(instance.order_items.all())
        RequestConfig(self.request).configure(products)
        RequestConfig(self.request).configure(order_items)
        context.update(locals())
        return context

@method_decorator(staff_member_required, name='dispatch')
class ResourcePlanUpdateView(UpdateView):
    model = ResourcePlan
    template_name = 'order_update.html'
    form_class = ResourcePlanEditForm


def get_success_url(self):
   return reverse('update_order', kwargs={'pk': self.object.id})

def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.object
        qs_p = Resource.objects.filter(active=True)[:12]
        products = ResourceTable(qs_p)
        order_items = ResourcePlanItemTable(instance.order_items.all())
        RequestConfig(self.request).configure(products)
        RequestConfig(self.request).configure(order_items)
        context.update(locals())
        return context

@staff_member_required
def ajax_search_products(request, pk):
    instance = get_object_or_404(ResourcePlan, id=pk)
    q = request.GET.get('q', None)
    products = Resource.broswer.active().filter(title__startswith=q) if q else Resource.broswer.active()
    products = products[:12]
    products = ResourceTable(products)
    RequestConfig(request).configure(products)
    data = dict()
    data['products'] = render_to_string(template_name='include/product_container.html',
                                        request=request,
                                        context={
                                            'products': products,
                                            'instance': instance
                                        })
    return JsonResponse(data)

@staff_member_required
def ajax_add_product(request, pk, dk):
    instance = get_object_or_404(ResourcePlan, id=pk)
    product = get_object_or_404(Resource, id=dk)
    order_item, created = ResourcePlanItem.objects.get_or_create(order=instance, product=product)
    if created:
        order_item.qty = 1
        order_item.price = product.value
        order_item.discount_price = product.discount_value
    else:
        order_item.qty += 1
    order_item.save()
    product.qty -= 1
    product.save()
    instance.refresh_from_db()
    order_items = ResourcePlanItemTable(instance.order_items.all())
    RequestConfig(request).configure(order_items)
    data = dict()
    data['result'] = render_to_string(template_name='include/order_container.html',
                                      request=request,
                                      context={'instance': instance,
                                               'order_items': order_items
                                               }
                                    )
    return JsonResponse(data)

@staff_member_required
def ajax_modify_order_item(request, pk, action):
    order_item = get_object_or_404(ResourcePlanItem, id=pk)
    product = order_item.product
    instance = order_item.order
    if action == 'remove':
        order_item.qty -= 1
        product.qty += 1
        if order_item.qty < 1: order_item.qty = 1
    if action == 'add':
        order_item.qty += 1
        product.qty -= 1
    product.save()
    order_item.save()
    if action == 'delete':
        order_item.delete()
    data = dict()
    instance.refresh_from_db()
    order_items = ResourcePlanItemTable(instance.order_items.all())
    RequestConfig(request).configure(order_items)
    data['result'] = render_to_string(template_name='include/order_container.html',
                                      request=request,
                                      context={
                                          'instance': instance,
                                          'order_items': order_items
                                      }
                                      )
    return JsonResponse(data)


    @staff_member_required
def delete_order(request, pk):
    instance = get_object_or_404(ResourcePlan, id=pk)
    instance.delete()
    messages.warning(request, 'The order is deleted!')
    return redirect(reverse('homepage'))


@staff_member_required
def done_order_view(request, pk):
    instance = get_object_or_404(ResourcePlan, id=pk)
    instance.is_paid = True
    instance.save()
    return redirect(reverse('homepage'))

    