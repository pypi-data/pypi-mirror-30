from controlcenter import Dashboard, widgets


class EmptyDashboard(Dashboard):
    pass


class MyWidget0(widgets.Widget):
    pass


class MyWidget1(widgets.Widget):
    pass


class NonEmptyDashboard(Dashboard):
    widgets = [
        MyWidget0,
        widgets.Group([MyWidget1])
    ]
