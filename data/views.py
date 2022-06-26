import pandas as pd
import numpy as np
from django.views.generic import TemplateView
from .methods import csv_to_db
from .models import Purchase
from .charts import objects_to_df, qs_to_df, Chart
from psm.models import Project
from psm.views import get_filter_options


PALETTE = ['#465b65', '#184c9c', '#d33035', '#ffc107', '#28a745', '#6f7f8c', '#6610f2', '#6e9fa5', '#fd7e14', '#e83e8c', '#17a2b8', '#6f42c1' ]

class Dashboard(TemplateView):
    template_name = 'data/dashboard.html'

    def get_context_data(self, **kwargs):

        # get the data from the default method
        context = super().get_context_data(**kwargs)

        get_filter_options(self, context, plan=False)

        # create a charts context to hold all of the charts
        context['charts'] = []

        q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }
        qs = Project.objects.filter(**q)

        df1 = qs_to_df(model=Project, qs=qs.filter(year__gte=2019,year__lte=2022),
            fields=['year', 'cf', 'CBUs__name', 'dept__div__name', 'type', 'counts', 'est_cost', 'budget'])

        proj_df1_1 = Chart('stackedBar', chart_id='proj_df1_1', palette=PALETTE)
        proj_df1_1.from_df(df1, values='counts', stacks=['type'], labels=['year'])
        context['charts'].append(proj_df1_1.get_presentation())

        proj_df1_2 = Chart('bar', chart_id='proj_df1_2', palette=PALETTE)
        proj_df1_2.from_df(df1, values='counts', stacks=['dept__div__name'], labels=['year'])
        context['charts'].append(proj_df1_2.get_presentation())

        # FIXME Boolean, Decimal type
        proj_df1_3 = Chart('stackedBar', chart_id='proj_df1_3', palette=PALETTE, title='Yearly trend (C/F=True)')
        proj_df1_3.from_df(df1, values='counts', stacks=['cf'], labels=['year'])
        context['charts'].append(proj_df1_3.get_presentation())

        df2 = qs_to_df(model=Project, qs=qs.filter(year=2022), 
            fields=['type', 'cf', 'dept__name', 'CBUs__name', 'phase', 'state', 'counts', 'est_cost', 'budget'])

        proj_df2_1 = Chart('stackedBar', chart_id='proj_df2_1', palette=PALETTE)
        proj_df2_1.from_df(df2, values='counts', stacks=['type'], labels=['CBUs__name'])
        context['charts'].append(proj_df2_1.get_presentation())


        proj_stat4 = Chart('stackedHorizontalBar', chart_id='proj_stat4', palette=PALETTE, height=100)
        proj_stat4.from_df(df2, values='counts', stacks=['phase'], labels=['dept__name'])
        context['charts'].append(proj_stat4.get_presentation())

        proj_stat5 = Chart('stackedHorizontalBar', chart_id='proj_stat5', palette=PALETTE, height=100)
        proj_stat5.from_df(df2, values='counts', stacks=['phase'], labels=['CBUs__name'])
        context['charts'].append(proj_stat5.get_presentation())

        proj_stat6 = Chart('stackedHorizontalBar', chart_id='proj_stat6', palette=PALETTE, height=100, title='C/F:True')
        proj_stat6.from_df(df2, values='counts', stacks=['cf'], labels=['CBUs__name'])
        context['charts'].append(proj_stat6.get_presentation())

        # date -> group by month
        df3 = qs_to_df(model=Project, qs=qs.filter(year=2022), 
            date_cols=['%m/%y', 'p_launch', 'p_kickoff'],
            fields=['type', 'dept__name', 'CBUs__name', 'p_launch', 'p_kickoff', 'phase', 'state', 'counts', 'est_cost', 'budget'])

        proj_stat2 = Chart('stackedBar', chart_id='proj_stat2', palette=PALETTE, title='Planned kickoff')
        proj_stat2.from_df(df3, values='counts', stacks=['type'], labels=['p_kickoff'])
        context['charts'].append(proj_stat2.get_presentation())

        proj_stat3 = Chart('stackedBar', chart_id='proj_stat3', palette=PALETTE, title='Planned Launch')
        proj_stat3.from_df(df3, values='counts', stacks=['type'], labels=['p_launch'])
        context['charts'].append(proj_stat3.get_presentation())


        proj_stat7 = Chart('HorizontalBar', chart_id='proj_stat7', palette=PALETTE, height=100, title='Proejct Est.Cost')
        proj_stat7.from_df(df3, values='est_cost', stacks=['phase'], labels=['CBUs__name'])
        context['charts'].append(proj_stat7.get_presentation())

        # data fill
        # csv_to_db()

        # the fields we will use
        # df_fields = ['city', 'customer_type', 'gender', 'unit_price', 'quantity', 
        #     'product_line', 'tax', 'total' , 'date', 'time', 'payment', 
        #     'cogs', 'profit', 'rating']

        # fields to exclude
        # df_exclude = ['id', 'cogs']
        
        # create a datframe with all the records.  chart.js doesn't deal well 
        # with dates in all situations so our method will convert them to strings
        # however we will need to identify the date columns and the format we want.
        # I am useing just month and year here.
        df = objects_to_df(Purchase, date_cols=['%Y-%m', 'date'])
        # df = qs_to_df(model=Purchase, qs=Purchase.objects.filter(gender='Female'), date_cols=['%Y-%m', 'date'])
    
        
        ### every chart is added the same way so I will just document the first one
        # create a chart object with a unique chart_id and color palette
        # if not chart_id or color palette is provided these will be randomly generated 
        # the type of charts does need to be identified here and might iffer from the chartjs type
        # create a pandas pivot_table based on the fields and aggregation we want
        # stacks are used for either grouping or stacking a certain column
        # add the presentation of the chart to the charts context

        # city_gender_h = Chart('stackedHorizontalBar', chart_id='city_gender_h', palette=PALETTE)
        # city_gender_h.from_df(df, values='total', stacks=['gender'], labels=['city'])
        # context['charts'].append(city_gender_h.get_presentation())

        # city_gender = Chart('stackedBar', chart_id='city_gender', palette=PALETTE)
        # city_gender.from_df(df, values='total', stacks=['gender'], labels=['city'])
        # context['charts'].append(city_gender.get_presentation())

        # exp_bar = Chart('bar', chart_id='bar01', palette=PALETTE)
        # exp_bar.from_df(df, values='total', labels=['city'])
        # context['charts'].append(exp_bar.get_presentation())

        # city_payment = Chart('groupedBar', chart_id='city_payment', palette=PALETTE)
        # city_payment.from_df(df, values='total', stacks=['payment'], labels=['date'])
        # context['charts'].append(city_payment.get_presentation())

        # city_payment_h = Chart('horizontalBar', chart_id='city_payment_h', palette=PALETTE)
        # city_payment_h.from_df(df, values='total', stacks=['payment'], labels=['city'])
        # context['charts'].append(city_payment_h.get_presentation())

        # city_payment_radar = Chart('radar', chart_id='city_payment_radar', palette=PALETTE)
        # city_payment_radar.from_df(df, values='total', stacks=['payment'], labels=['city'])
        # context['charts'].append(city_payment_radar.get_presentation())

        # exp_polar = Chart('polarArea', chart_id='polar01', palette=PALETTE, title='polarArea')
        # exp_polar.from_df(df, values='total', labels=['payment'])
        # context['charts'].append(exp_polar.get_presentation())

        # exp_doughnut = Chart('doughnut', chart_id='doughnut01', palette=PALETTE)
        # exp_doughnut.from_df(df, values='total', labels=['city'])
        # context['charts'].append(exp_doughnut.get_presentation())

        return context

