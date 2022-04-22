from pyecharts.charts import Line
import pyecharts.options as opts

interest = 0.1  # 年利率
monthly_save = 3000  # 一个月的存款
invest_years = 40  # 从 25 岁到 40 岁为 15 年
monthly_cost = 20000  # 财富自由后的每月支出

line = (
    Line(init_opts=opts.InitOpts(width="100%", height="1000px"))
    .add_xaxis(xaxis_data=[str(i) for i in range(0, invest_years, 5)])
    .set_global_opts(
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        # xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
    )
)

for monthly_save in range(3000, 10000, 2000):
    for interest in range(6, 12, 2):
        interest /= 100
        assets = 0.0
        yearly_data = []
        for i in range(invest_years):
            assets *= 1 + interest
            assets += monthly_save * 12
            if i % 5 == 0:
                yearly_data.append(int(assets))
        line.add_yaxis(
            series_name=f"{monthly_save}",
            y_axis=yearly_data,
            label_opts=opts.LabelOpts(is_show=False),
        )
        if assets * interest / 12 >= monthly_cost:
            print(monthly_save)
            print(assets)
            # break

line.render("test.html")
